"""
Scoring API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from pydantic import BaseModel

from app.services.scoring_service import ScoringService
from app.models.scoring import MatchFormat, ScoreUpdate, GameSituation, LiveBroadcastData
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


@router.get("/matches/{match_id}/live")
async def get_live_broadcast_data(
    match_id: str,
    player1_name: str,
    player2_name: str,
    player1_ranking: Optional[int] = None,
    player2_ranking: Optional[int] = None,
    player1_country: Optional[str] = None,
    player2_country: Optional[str] = None,
    last_points: int = 5,
    current_user: User = Depends(get_current_user)
):
    """
    Get optimized live broadcast data package

    Returns comprehensive data for live streaming/broadcast in a single request:
    - Scoreboard: Visual scoreboard with player info
    - Situation: Current game situation (break point, set point, etc.)
    - Last Points: Recent points summary (default: last 5)
    - Key Stats: Essential statistics (aces, winners, errors, etc.)
    - Timestamp: Data freshness indicator

    Optimized for minimal latency and bandwidth usage.
    Ideal for:
    - Live streaming overlays
    - Real-time scoreboards
    - Mobile apps
    - TV broadcasts

    Query params:
    - player1_name, player2_name: Player names (required)
    - player1_ranking, player2_ranking: Rankings (optional)
    - player1_country, player2_country: Country codes (optional)
    - last_points: Number of recent points to include (default: 5, max: 20)
    """
    service = ScoringService()

    # Validate last_points parameter
    if last_points < 1 or last_points > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="last_points must be between 1 and 20"
        )

    try:
        data = await service.get_live_broadcast_data(
            match_id=match_id,
            player1_name=player1_name,
            player2_name=player2_name,
            player1_ranking=player1_ranking,
            player2_ranking=player2_ranking,
            player1_country=player1_country,
            player2_country=player2_country,
            last_points_count=last_points
        )
        return data.model_dump()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get live broadcast data: {str(e)}"
        )


@router.get("/matches/{match_id}/broadcast")
async def get_broadcast_score(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get minimal broadcast overlay score

    Returns ultra-compact score data optimized for TV/streaming overlays.
    Includes only essential info:
    - Current game score (0, 15, 30, 40, AD or tiebreak points)
    - Sets won by each player
    - Current set games
    - Completed sets with tiebreak notation
    - Server indicator (p1 or p2)
    - Match completion status

    Perfect for:
    - Minimal bandwidth scenarios
    - Simple overlay graphics
    - Frequent polling (low latency)
    - Mobile data conservation

    Response format uses compact keys (p1/p2) to minimize payload size.
    """
    service = ScoringService()

    try:
        score = await service.get_broadcast_score(match_id)
        return score
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get broadcast score: {str(e)}"
        )


@router.get("/matches/{match_id}/export")
async def export_match_data(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Export complete match data for analysis/archival

    Returns comprehensive match package including:
    - Full match score (all sets, games, points)
    - Complete point history with detailed information
    - Aggregated statistics (aces, winners, errors, break points, etc.)
    - Timeline of key events (break points, set points, match points)
    - Match metadata (format, winner, completion status)
    - Export timestamp

    Use cases:
    - Post-match analysis
    - Historical archival
    - Data analytics
    - Machine learning training data
    - Detailed reporting

    Warning: Response can be large for long matches (100+ KB).
    Not recommended for real-time polling.
    """
    service = ScoringService()

    try:
        data = await service.export_complete_match_data(match_id)
        return data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export match data: {str(e)}"
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
