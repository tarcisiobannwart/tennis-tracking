"""
Rankings API routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.sql import User
from app.services.ranking_service import RankingService
from app.schemas.ranking import (
    RankingCreate,
    RankingUpdate,
    RankingResponse,
    RankingListResponse,
    RankingDetailResponse,
    RankingParticipantCreate,
    RankingParticipantResponse,
    RankingRoundCreate,
    RankingRoundUpdate,
    RankingRoundResponse,
    RankingMatchCreate,
    RankingMatchUpdate,
    RankingMatchResponse,
    StandingsResponse,
)

router = APIRouter()


@router.get("/", response_model=RankingListResponse)
async def get_rankings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    ranking_type: Optional[str] = None,
    organization_id: Optional[str] = None,
    my_rankings: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated rankings with optional filters"""

    service = RankingService(db)
    skip = (page - 1) * limit

    user_id = current_user.id if my_rankings else None

    rankings, total = await service.get_rankings(
        skip=skip,
        limit=limit,
        status=status,
        ranking_type=ranking_type,
        organization_id=organization_id,
        user_id=user_id,
    )

    # Get participant counts for each ranking
    ranking_responses = []
    for ranking in rankings:
        participants = await service.get_participants(ranking.id)
        ranking_dict = {
            **ranking.__dict__,
            "total_participants": len(participants),
        }
        ranking_responses.append(RankingResponse(**ranking_dict))

    return RankingListResponse(
        data=ranking_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
    )


@router.post("/", response_model=RankingResponse, status_code=201)
async def create_ranking(
    ranking_data: RankingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new ranking"""

    service = RankingService(db)
    ranking = await service.create_ranking(ranking_data, created_by=current_user.id)

    participants = await service.get_participants(ranking.id)
    ranking_dict = {
        **ranking.__dict__,
        "total_participants": len(participants),
    }

    return RankingResponse(**ranking_dict)


@router.get("/{ranking_id}", response_model=RankingDetailResponse)
async def get_ranking(
    ranking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single ranking by ID with detailed info"""

    service = RankingService(db)
    ranking = await service.get_ranking(ranking_id)

    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")

    participants = await service.get_participants(ranking_id)

    # Find current user's stats
    my_position = None
    my_stats = None
    for participant in participants:
        if participant.user_id == current_user.id:
            my_position = participant.position
            my_stats = {
                "position": participant.position,
                "previous_position": participant.previous_position,
                "points": participant.points,
                "matches_played": participant.matches_played,
                "matches_won": participant.matches_won,
                "matches_lost": participant.matches_lost,
                "matches_drawn": participant.matches_drawn,
                "sets_won": participant.sets_won,
                "sets_lost": participant.sets_lost,
                "games_won": participant.games_won,
                "games_lost": participant.games_lost,
                "position_history": participant.position_history or [],
                "win_rate": (
                    (participant.matches_won / participant.matches_played * 100)
                    if participant.matches_played > 0
                    else 0.0
                ),
                "set_ratio": (
                    (participant.sets_won / participant.sets_lost)
                    if participant.sets_lost > 0
                    else float(participant.sets_won)
                ),
            }
            break

    ranking_dict = {
        **ranking.__dict__,
        "total_participants": len(participants),
        "my_position": my_position,
        "my_stats": my_stats,
    }

    return RankingDetailResponse(**ranking_dict)


@router.put("/{ranking_id}", response_model=RankingResponse)
async def update_ranking(
    ranking_id: str,
    ranking_data: RankingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a ranking"""

    service = RankingService(db)
    ranking = await service.update_ranking(ranking_id, ranking_data)

    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")

    participants = await service.get_participants(ranking.id)
    ranking_dict = {
        **ranking.__dict__,
        "total_participants": len(participants),
    }

    return RankingResponse(**ranking_dict)


@router.delete("/{ranking_id}", status_code=204)
async def delete_ranking(
    ranking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a ranking"""

    service = RankingService(db)
    success = await service.delete_ranking(ranking_id)

    if not success:
        raise HTTPException(status_code=404, detail="Ranking not found")


# Participants endpoints
@router.post("/{ranking_id}/participants", response_model=RankingParticipantResponse, status_code=201)
async def add_participant(
    ranking_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a participant to a ranking"""

    service = RankingService(db)
    participant_data = RankingParticipantCreate(ranking_id=ranking_id, user_id=user_id)
    participant = await service.add_participant(participant_data)

    return RankingParticipantResponse(**participant.__dict__)


@router.get("/{ranking_id}/participants", response_model=List[RankingParticipantResponse])
async def get_participants(
    ranking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all participants in a ranking"""

    service = RankingService(db)
    participants = await service.get_participants(ranking_id)

    return [RankingParticipantResponse(**p.__dict__) for p in participants]


@router.delete("/participants/{participant_id}", status_code=204)
async def remove_participant(
    participant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a participant from a ranking"""

    service = RankingService(db)
    success = await service.remove_participant(participant_id)

    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")


# Rounds endpoints
@router.get("/{ranking_id}/rounds", response_model=List[RankingRoundResponse])
async def get_rounds(
    ranking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all rounds in a ranking"""

    service = RankingService(db)
    rounds = await service.get_rounds(ranking_id)

    # Add match counts for each round
    round_responses = []
    for round_obj in rounds:
        matches = await service.get_matches(round_id=round_obj.id)
        completed_matches = sum(1 for m in matches if m.status == "completed")

        round_dict = {
            **round_obj.__dict__,
            "total_matches": len(matches),
            "completed_matches": completed_matches,
        }
        round_responses.append(RankingRoundResponse(**round_dict))

    return round_responses


@router.post("/{ranking_id}/rounds", response_model=RankingRoundResponse, status_code=201)
async def create_round(
    ranking_id: str,
    round_data: RankingRoundCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new round in a ranking"""

    service = RankingService(db)

    # Override ranking_id from path
    round_data.ranking_id = ranking_id

    round_obj = await service.create_round(round_data)

    return RankingRoundResponse(**round_obj.__dict__, total_matches=0, completed_matches=0)


@router.put("/rounds/{round_id}", response_model=RankingRoundResponse)
async def update_round(
    round_id: str,
    round_data: RankingRoundUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a round"""

    service = RankingService(db)
    round_obj = await service.update_round(round_id, round_data)

    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")

    matches = await service.get_matches(round_id=round_id)
    completed_matches = sum(1 for m in matches if m.status == "completed")

    round_dict = {
        **round_obj.__dict__,
        "total_matches": len(matches),
        "completed_matches": completed_matches,
    }

    return RankingRoundResponse(**round_dict)


# Matches endpoints
@router.get("/{ranking_id}/matches", response_model=List[RankingMatchResponse])
async def get_matches(
    ranking_id: str,
    round_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get matches for a ranking or specific round"""

    service = RankingService(db)
    matches = await service.get_matches(ranking_id=ranking_id, round_id=round_id)

    return [RankingMatchResponse(**m.__dict__) for m in matches]


@router.post("/{ranking_id}/matches", response_model=RankingMatchResponse, status_code=201)
async def create_match(
    ranking_id: str,
    match_data: RankingMatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new ranking match"""

    service = RankingService(db)

    # Override ranking_id from path
    match_data.ranking_id = ranking_id

    match = await service.create_match(match_data)

    return RankingMatchResponse(**match.__dict__)


@router.put("/matches/{match_id}", response_model=RankingMatchResponse)
async def update_match(
    match_id: str,
    match_data: RankingMatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a ranking match"""

    service = RankingService(db)
    match = await service.update_match(match_id, match_data)

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return RankingMatchResponse(**match.__dict__)


# Standings endpoint
@router.get("/{ranking_id}/standings", response_model=StandingsResponse)
async def get_standings(
    ranking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current standings for a ranking"""

    service = RankingService(db)

    try:
        standings = await service.get_standings(ranking_id)
        return standings
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
