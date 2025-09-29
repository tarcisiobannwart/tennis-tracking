"""
Player API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import PlayerNotFoundException
from app.schemas.player import (
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PlayerStats,
    PlayerProfile
)
from app.schemas.match import MatchResponse
from app.services.player_service import PlayerService
from app.services.analytics_service import AnalyticsService
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", response_model=List[PlayerResponse])
async def list_players(
    skip: int = Query(0, ge=0, description="Number of players to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of players to return"),
    search: Optional[str] = Query(None, description="Search players by name"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    skill_level: Optional[str] = Query(None, description="Filter by skill level"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of players with optional filtering
    """
    logger.info("Fetching players", skip=skip, limit=limit, search=search)

    player_service = PlayerService(db)
    players = await player_service.get_players(
        skip=skip,
        limit=limit,
        search=search,
        country=country,
        skill_level=skill_level,
        is_active=is_active
    )

    return players


@router.get("/{player_id}", response_model=PlayerProfile)
async def get_player(
    player_id: str = Path(..., description="Player ID"),
    include_stats: bool = Query(True, description="Include player statistics"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific player by ID with optional statistics
    """
    logger.info("Fetching player", player_id=player_id, include_stats=include_stats)

    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)

    if not player:
        raise PlayerNotFoundException(player_id)

    if include_stats:
        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_player_statistics(player_id)
        player.stats = stats

    return player


@router.post("/", response_model=PlayerResponse)
async def create_player(
    player_data: PlayerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new player
    """
    logger.info("Creating player", name=player_data.name)

    player_service = PlayerService(db)
    player = await player_service.create_player(player_data)

    logger.info("Player created", player_id=player.id)
    return player


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: str = Path(..., description="Player ID"),
    player_data: PlayerUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing player
    """
    logger.info("Updating player", player_id=player_id)

    player_service = PlayerService(db)
    player = await player_service.update_player(player_id, player_data)

    if not player:
        raise PlayerNotFoundException(player_id)

    logger.info("Player updated", player_id=player_id)
    return player


@router.delete("/{player_id}")
async def delete_player(
    player_id: str = Path(..., description="Player ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a player (soft delete - sets is_active to False)
    """
    logger.info("Deleting player", player_id=player_id)

    player_service = PlayerService(db)
    success = await player_service.delete_player(player_id)

    if not success:
        raise PlayerNotFoundException(player_id)

    logger.info("Player deleted", player_id=player_id)
    return {"message": "Player deleted successfully"}


@router.get("/{player_id}/stats", response_model=PlayerStats)
async def get_player_stats(
    player_id: str = Path(..., description="Player ID"),
    period: Optional[str] = Query("all", description="Time period: 'all', 'year', 'month'"),
    surface: Optional[str] = Query(None, description="Filter by court surface"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed statistics for a player
    """
    logger.info("Fetching player stats", player_id=player_id, period=period, surface=surface)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    # Get statistics
    analytics_service = AnalyticsService(db)
    stats = await analytics_service.get_player_statistics(
        player_id,
        period=period,
        surface=surface
    )

    return stats


@router.get("/{player_id}/matches", response_model=List[MatchResponse])
async def get_player_matches(
    player_id: str = Path(..., description="Player ID"),
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
    limit: int = Query(50, ge=1, le=500, description="Number of matches to return"),
    status: Optional[str] = Query(None, description="Filter by match status"),
    surface: Optional[str] = Query(None, description="Filter by court surface"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get matches for a specific player
    """
    logger.info("Fetching player matches", player_id=player_id, skip=skip, limit=limit)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    # Get matches
    matches = await player_service.get_player_matches(
        player_id,
        skip=skip,
        limit=limit,
        status=status,
        surface=surface
    )

    return matches


@router.get("/{player_id}/recent-form")
async def get_player_recent_form(
    player_id: str = Path(..., description="Player ID"),
    matches: int = Query(10, ge=1, le=50, description="Number of recent matches"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent form for a player (W/L record)
    """
    logger.info("Fetching player recent form", player_id=player_id, matches=matches)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    # Get recent form
    form = await player_service.get_recent_form(player_id, matches)

    return {
        "player_id": player_id,
        "recent_matches": matches,
        "form": form["results"],
        "wins": form["wins"],
        "losses": form["losses"],
        "win_percentage": form["win_percentage"]
    }


@router.get("/{player_id}/head-to-head/{opponent_id}")
async def get_head_to_head(
    player_id: str = Path(..., description="Player ID"),
    opponent_id: str = Path(..., description="Opponent ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get head-to-head record between two players
    """
    logger.info("Fetching head-to-head", player_id=player_id, opponent_id=opponent_id)

    # Verify both players exist
    player_service = PlayerService(db)
    player1 = await player_service.get_player(player_id)
    player2 = await player_service.get_player(opponent_id)

    if not player1:
        raise PlayerNotFoundException(player_id)
    if not player2:
        raise PlayerNotFoundException(opponent_id)

    # Get head-to-head record
    analytics_service = AnalyticsService(db)
    h2h = await analytics_service.get_head_to_head(player_id, opponent_id)

    return h2h


@router.get("/search/ranking")
async def search_players_by_ranking(
    min_ranking: Optional[int] = Query(None, description="Minimum ranking"),
    max_ranking: Optional[int] = Query(None, description="Maximum ranking"),
    limit: int = Query(50, ge=1, le=500, description="Number of players to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search players by ranking range
    """
    logger.info("Searching players by ranking", min_ranking=min_ranking, max_ranking=max_ranking)

    player_service = PlayerService(db)
    players = await player_service.search_by_ranking(
        min_ranking=min_ranking,
        max_ranking=max_ranking,
        limit=limit
    )

    return players