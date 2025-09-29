"""
Matches API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import uuid

from app.core.mongodb import get_database
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_matches(page: int = 1, limit: int = 20):
    """Get paginated matches"""
    db = get_database()

    # Calculate skip value
    skip = (page - 1) * limit

    try:
        # Get matches with pagination
        matches = await db.matches.find({}).skip(skip).limit(limit).sort("createdAt", -1).to_list(limit)

        # Get total count
        total = await db.matches.count_documents({})

        # Format response
        formatted_matches = []
        for match in matches:
            formatted_matches.append({
                "id": str(match["_id"]),
                "player1": match.get("player1", "Player 1"),
                "player2": match.get("player2", "Player 2"),
                "score": match.get("score", "0-0"),
                "status": match.get("status", "completed"),
                "date": match.get("createdAt", datetime.utcnow()).isoformat(),
                "duration": match.get("duration", "00:00:00"),
                "court": match.get("court", "Center Court"),
                "tournament": match.get("tournament", "Training Match")
            })

        # If no matches in database, return sample data
        if not formatted_matches:
            formatted_matches = [
                {
                    "id": str(ObjectId()),
                    "player1": "Rafael Nadal",
                    "player2": "Novak Djokovic",
                    "score": "6-4, 7-5",
                    "status": "completed",
                    "date": datetime.utcnow().isoformat(),
                    "duration": "02:15:00",
                    "court": "Center Court",
                    "tournament": "Demo Match"
                },
                {
                    "id": str(ObjectId()),
                    "player1": "Roger Federer",
                    "player2": "Andy Murray",
                    "score": "7-6, 6-3",
                    "status": "completed",
                    "date": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                    "duration": "01:45:00",
                    "court": "Court 1",
                    "tournament": "Exhibition"
                }
            ]
            total = len(formatted_matches)

        return {
            "data": formatted_matches,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": (total + limit - 1) // limit
        }
    except Exception as e:
        # Return sample data on error
        sample_matches = [
            {
                "id": str(ObjectId()),
                "player1": "Rafael Nadal",
                "player2": "Novak Djokovic",
                "score": "6-4, 7-5",
                "status": "completed",
                "date": datetime.utcnow().isoformat(),
                "duration": "02:15:00",
                "court": "Center Court",
                "tournament": "Demo Match"
            }
        ]
        return {
            "data": sample_matches,
            "total": 1,
            "page": page,
            "limit": limit,
            "totalPages": 1
        }


@router.get("/live")
async def get_live_matches():
    """Get live matches"""
    db = get_database()

    # Por enquanto, retorna lista vazia (sem partidas ao vivo)
    # Em produção, isso seria integrado com sistema de streaming
    return []


@router.get("/recent")
async def get_recent_matches(limit: int = 5):
    """Get recent matches"""
    db = get_database()

    # Busca partidas recentes
    recent_date = datetime.utcnow() - timedelta(days=7)

    matches = await db.matches.find({
        "createdAt": {"$gte": recent_date}
    }).sort("createdAt", -1).limit(limit).to_list(limit)

    # Formata resposta
    formatted_matches = []
    for match in matches:
        formatted_matches.append({
            "id": str(match["_id"]),
            "player1": match.get("player1", "Player 1"),
            "player2": match.get("player2", "Player 2"),
            "score": match.get("score", "0-0"),
            "status": match.get("status", "completed"),
            "date": match.get("createdAt", datetime.utcnow()).isoformat(),
            "duration": match.get("duration", "00:00:00"),
            "court": match.get("court", "Center Court"),
            "tournament": match.get("tournament", "Training Match")
        })

    # Se não houver partidas, retorna dados de exemplo
    if not formatted_matches:
        formatted_matches = [
            {
                "id": str(ObjectId()),
                "player1": "Rafael Nadal",
                "player2": "Novak Djokovic",
                "score": "6-4, 7-5",
                "status": "completed",
                "date": datetime.utcnow().isoformat(),
                "duration": "02:15:00",
                "court": "Center Court",
                "tournament": "Demo Match"
            },
            {
                "id": str(ObjectId()),
                "player1": "Roger Federer",
                "player2": "Andy Murray",
                "score": "7-6, 6-3",
                "status": "completed",
                "date": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                "duration": "01:45:00",
                "court": "Court 1",
                "tournament": "Exhibition"
            }
        ]

    return formatted_matches


@router.post("/")
async def create_match(
    player1: str,
    player2: str,
    tournament: Optional[str] = "Training Match",
    court: Optional[str] = "Main Court",
    current_user=Depends(get_current_user)
):
    """Create a new match"""
    db = get_database()

    match = {
        "_id": ObjectId(),
        "matchId": str(uuid.uuid4()),
        "player1": player1,
        "player2": player2,
        "tournament": tournament,
        "court": court,
        "userId": str(current_user["_id"]),
        "status": "scheduled",
        "score": "0-0",
        "sets": [],
        "statistics": {
            "player1": {
                "aces": 0,
                "double_faults": 0,
                "winners": 0,
                "unforced_errors": 0
            },
            "player2": {
                "aces": 0,
                "double_faults": 0,
                "winners": 0,
                "unforced_errors": 0
            }
        },
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    result = await db.matches.insert_one(match)

    return {
        "id": str(result.inserted_id),
        "matchId": match["matchId"],
        "message": "Match created successfully"
    }


@router.get("/{match_id}")
async def get_match(match_id: str, current_user=Depends(get_current_user)):
    """Get match details"""
    db = get_database()

    # Tenta buscar por ObjectId ou matchId
    try:
        match = await db.matches.find_one({"_id": ObjectId(match_id)})
    except:
        match = await db.matches.find_one({"matchId": match_id})

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Formata resposta
    return {
        "id": str(match["_id"]),
        "matchId": match.get("matchId"),
        "player1": match.get("player1"),
        "player2": match.get("player2"),
        "score": match.get("score"),
        "sets": match.get("sets", []),
        "status": match.get("status"),
        "tournament": match.get("tournament"),
        "court": match.get("court"),
        "statistics": match.get("statistics", {}),
        "createdAt": match.get("createdAt"),
        "updatedAt": match.get("updatedAt")
    }


@router.patch("/{match_id}/score")
async def update_match_score(
    match_id: str,
    score: str,
    current_user=Depends(get_current_user)
):
    """Update match score"""
    db = get_database()

    # Atualiza score
    result = await db.matches.update_one(
        {"_id": ObjectId(match_id)},
        {
            "$set": {
                "score": score,
                "updatedAt": datetime.utcnow()
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Match not found")

    return {"message": "Score updated successfully"}


@router.patch("/{match_id}/status")
async def update_match_status(
    match_id: str,
    status: str,
    current_user=Depends(get_current_user)
):
    """Update match status"""
    db = get_database()

    # Valida status
    valid_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # Atualiza status
    result = await db.matches.update_one(
        {"_id": ObjectId(match_id)},
        {
            "$set": {
                "status": status,
                "updatedAt": datetime.utcnow()
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Match not found")

    return {"message": "Status updated successfully"}


@router.delete("/{match_id}")
async def delete_match(match_id: str, current_user=Depends(get_current_user)):
    """Delete a match"""
    db = get_database()

    result = await db.matches.delete_one({
        "_id": ObjectId(match_id),
        "userId": str(current_user["_id"])
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Match not found or not authorized")

    return {"message": "Match deleted successfully"}