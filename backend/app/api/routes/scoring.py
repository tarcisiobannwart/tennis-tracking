"""
Scoring API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from pydantic import BaseModel

from app.services.scoring_service import ScoringService
from app.models.scoring import MatchFormat, ScoreUpdate, GameSituation
from app.models.scoreboard import ScoreboardStyle
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/scoring", tags=["scoring"])


# Request/Response schemas
class CreateMatchScoreRequest(BaseModel):
    """Request to create a new match score"""
    match_id: str
    player1_id: str
    player2_id: str
    format: MatchFormat = MatchFormat.BEST_OF_3
    starting_server_id: Optional[str] = None


class AddPointRequest(BaseModel):
    """Request to add a point"""
    winner_player_id: str


# Endpoints
@router.post("/matches", status_code=status.HTTP_201_CREATED)
async def create_match_score(
    request: CreateMatchScoreRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new match score

    Initializes a new match with:
    - Match format (best of 3 or 5)
    - Player IDs
    - Starting server
    - First set and game
    """
    service = ScoringService()

    try:
        match_score = await service.create_match_score(
            match_id=request.match_id,
            player1_id=request.player1_id,
            player2_id=request.player2_id,
            format=request.format,
            starting_server_id=request.starting_server_id
        )

        return {
            "message": "Match score created successfully",
            "match_id": match_score.match_id,
            "format": match_score.format.value,
            "current_server_id": match_score.current_server_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create match score: {str(e)}"
        )


@router.get("/matches/{match_id}")
async def get_match_score(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get current match score

    Returns complete score including:
    - All completed sets
    - Current set in progress
    - Current game score (0, 15, 30, 40, AD)
    - Current server
    - Match status (complete/in-progress)
    """
    service = ScoringService()

    try:
        score_display = await service.get_current_score_display(match_id)
        return score_display
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match score: {str(e)}"
        )


@router.post("/matches/{match_id}/points", status_code=status.HTTP_200_OK)
async def add_point(
    match_id: str,
    request: AddPointRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Add a point to the match

    Implements full ATP/WTA scoring rules:
    - Points: 0 → 15 → 30 → 40 → game
    - Deuce and advantage at 40-40
    - Tiebreak: first to 7, win by 2
    - Sets: first to 6 games, win by 2
    - Server alternation

    Returns events that occurred (point_won, game_won, set_won, match_won)
    """
    service = ScoringService()

    try:
        score_update = await service.add_point(match_id, request.winner_player_id)

        return {
            "message": "Point added successfully",
            "match_id": score_update.match_id,
            "point_winner_id": score_update.point_winner_id,
            "timestamp": score_update.timestamp,
            "events": score_update.events,
            "situation": score_update.situation.model_dump() if score_update.situation else None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add point: {str(e)}"
        )


@router.get("/matches/{match_id}/stats")
async def get_match_stats(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get match statistics

    Returns:
    - Sets won by each player
    - Total games won
    - Current set number
    - Match format
    - Completion status
    """
    service = ScoringService()

    try:
        stats = await service.get_match_stats(match_id)
        return stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match stats: {str(e)}"
        )


@router.get("/matches/{match_id}/scoreboard")
async def get_scoreboard(
    match_id: str,
    player1_name: str,
    player2_name: str,
    style: ScoreboardStyle = ScoreboardStyle.TRADITIONAL,
    player1_ranking: Optional[int] = None,
    player2_ranking: Optional[int] = None,
    player1_country: Optional[str] = None,
    player2_country: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get visual scoreboard for match

    Returns scoreboard with:
    - Player names (auto-abbreviated: R. FEDERER)
    - Current score (points, games, sets)
    - Completed sets with tiebreak notation
    - Serving indicator
    - Configurable style (TRADITIONAL, MODERN, TV_BROADCAST, MOBILE, COMPACT)

    Query params:
    - player1_name: Full player name (e.g., "Roger Federer")
    - player2_name: Full player name (e.g., "Rafael Nadal")
    - style: Display style (optional, default: TRADITIONAL)
    - player1_ranking: Player 1 ranking (optional)
    - player2_ranking: Player 2 ranking (optional)
    - player1_country: Player 1 country code (optional, e.g., "SUI")
    - player2_country: Player 2 country code (optional, e.g., "ESP")
    """
    service = ScoringService()

    try:
        scoreboard = await service.get_scoreboard(
            match_id=match_id,
            player1_name=player1_name,
            player2_name=player2_name,
            style=style,
            player1_ranking=player1_ranking,
            player2_ranking=player2_ranking,
            player1_country=player1_country,
            player2_country=player2_country
        )
        return scoreboard
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scoreboard: {str(e)}"
        )


@router.get("/matches/{match_id}/situation")
async def get_game_situation(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get current game situation with special conditions detection

    Returns comprehensive situation analysis:
    - is_break_point: Receiver one point from breaking serve
    - is_set_point: Player one point from winning set
    - is_match_point: Player one point from winning match
    - is_deuce: Game at deuce (40-40)
    - is_advantage: One player has advantage
    - is_tiebreak: Currently in tiebreak
    - is_bagel_possible: Possible 6-0 set (bagel)
    - is_breadstick_possible: Possible 6-1 set (breadstick)
    - situation_text: Human-readable description

    Special situations detected:
    - Break Point: Receiver is one point from winning server's game
    - Set Point: Player needs 1 point to win set (5+ games or tiebreak 6+)
    - Match Point: Player needs 1 point to win match (already has sets_needed-1 sets)
    - Deuce: Both players at 40-40
    - Advantage: One player at 40+ after deuce
    - Tiebreak: Players at 6-6 in games
    - Bagel: Leading 5-0 (possible 6-0 set)
    - Breadstick: Leading 5-1 (possible 6-1 set)
    """
    service = ScoringService()

    try:
        situation = await service.get_game_situation(match_id)
        return situation.model_dump()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get game situation: {str(e)}"
        )


@router.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match_score(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a match score"""
    service = ScoringService()

    try:
        deleted = await service.delete_match_score(match_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match score not found: {match_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete match score: {str(e)}"
        )
