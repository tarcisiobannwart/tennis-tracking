"""
Analytics API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import MatchNotFoundException, PlayerNotFoundException
from app.schemas.analytics import (
    PerformanceAnalytics,
    HeatmapData,
    PlayerComparison,
    TrendAnalysis,
    MatchInsights
)
from app.services.analytics_service import AnalyticsService
from app.services.match_service import MatchService
from app.services.player_service import PlayerService
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/performance/{match_id}", response_model=List[PerformanceAnalytics])
async def get_match_performance(
    match_id: str = Path(..., description="Match ID"),
    player_id: Optional[str] = Query(None, description="Specific player ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance analytics for a match
    """
    logger.info("Fetching match performance analytics", match_id=match_id, player_id=player_id)

    # Verify match exists
    match_service = MatchService(db)
    match = await match_service.get_match(match_id)
    if not match:
        raise MatchNotFoundException(match_id)

    analytics_service = AnalyticsService(db)
    performance_data = await analytics_service.get_match_performance_analytics(
        match_id, player_id
    )

    return performance_data


@router.get("/heatmap/{match_id}", response_model=List[HeatmapData])
async def get_match_heatmap(
    match_id: str = Path(..., description="Match ID"),
    player_id: Optional[str] = Query(None, description="Specific player ID"),
    data_type: str = Query("position", description="Heatmap type: position, shots, serves, returns"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get heatmap data for a match
    """
    logger.info("Fetching match heatmap", match_id=match_id, data_type=data_type)

    # Verify match exists
    match_service = MatchService(db)
    match = await match_service.get_match(match_id)
    if not match:
        raise MatchNotFoundException(match_id)

    analytics_service = AnalyticsService(db)
    heatmap_data = await analytics_service.get_match_heatmap_data(
        match_id, player_id, data_type
    )

    return heatmap_data


@router.get("/comparison", response_model=PlayerComparison)
async def compare_players(
    player1_id: str = Query(..., description="First player ID"),
    player2_id: str = Query(..., description="Second player ID"),
    period: str = Query("career", description="Comparison period: match, season, career"),
    surface: Optional[str] = Query(None, description="Filter by court surface"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare two players' performance
    """
    logger.info("Comparing players", player1_id=player1_id, player2_id=player2_id, period=period)

    # Verify both players exist
    player_service = PlayerService(db)
    player1 = await player_service.get_player(player1_id)
    player2 = await player_service.get_player(player2_id)

    if not player1:
        raise PlayerNotFoundException(player1_id)
    if not player2:
        raise PlayerNotFoundException(player2_id)

    analytics_service = AnalyticsService(db)
    comparison = await analytics_service.compare_players(
        player1_id, player2_id, period, surface
    )

    return comparison


@router.get("/trends/{player_id}", response_model=List[TrendAnalysis])
async def get_player_trends(
    player_id: str = Path(..., description="Player ID"),
    metrics: List[str] = Query(
        ["win_percentage", "serve_percentage", "unforced_errors"],
        description="Metrics to analyze trends for"
    ),
    period: str = Query("month", description="Time period: week, month, quarter, year"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trend analysis for a player
    """
    logger.info("Fetching player trends", player_id=player_id, metrics=metrics, period=period)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    analytics_service = AnalyticsService(db)
    trends = await analytics_service.get_player_trends(player_id, metrics, period)

    return trends


@router.get("/insights/{match_id}", response_model=MatchInsights)
async def get_match_insights(
    match_id: str = Path(..., description="Match ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated insights for a match
    """
    logger.info("Generating match insights", match_id=match_id)

    # Verify match exists
    match_service = MatchService(db)
    match = await match_service.get_match(match_id)
    if not match:
        raise MatchNotFoundException(match_id)

    analytics_service = AnalyticsService(db)
    insights = await analytics_service.generate_match_insights(match_id)

    return insights


@router.get("/player-stats/{player_id}")
async def get_advanced_player_stats(
    player_id: str = Path(..., description="Player ID"),
    period: str = Query("all", description="Time period: all, year, month"),
    surface: Optional[str] = Query(None, description="Filter by court surface"),
    opponent_ranking: Optional[int] = Query(None, description="Filter by opponent ranking"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get advanced statistics for a player with filtering options
    """
    logger.info("Fetching advanced player stats", player_id=player_id, period=period)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    analytics_service = AnalyticsService(db)
    stats = await analytics_service.get_advanced_player_stats(
        player_id, period, surface, opponent_ranking
    )

    return stats


@router.get("/rally-analysis/{match_id}")
async def get_rally_analysis(
    match_id: str = Path(..., description="Match ID"),
    min_length: int = Query(3, description="Minimum rally length"),
    max_length: Optional[int] = Query(None, description="Maximum rally length"),
    rally_type: Optional[str] = Query(None, description="Rally type filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed rally analysis for a match
    """
    logger.info("Fetching rally analysis", match_id=match_id, min_length=min_length)

    # Verify match exists
    match_service = MatchService(db)
    match = await match_service.get_match(match_id)
    if not match:
        raise MatchNotFoundException(match_id)

    analytics_service = AnalyticsService(db)
    rallies = await analytics_service.get_rally_analysis(
        match_id, min_length, max_length, rally_type
    )

    return rallies


@router.get("/serve-analysis/{match_id}")
async def get_serve_analysis(
    match_id: str = Path(..., description="Match ID"),
    player_id: Optional[str] = Query(None, description="Specific player ID"),
    serve_type: Optional[str] = Query(None, description="Serve type: first, second"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed serve analysis for a match
    """
    logger.info("Fetching serve analysis", match_id=match_id, player_id=player_id)

    # Verify match exists
    match_service = MatchService(db)
    match = await match_service.get_match(match_id)
    if not match:
        raise MatchNotFoundException(match_id)

    analytics_service = AnalyticsService(db)
    serves = await analytics_service.get_serve_analysis(match_id, player_id, serve_type)

    return serves


@router.get("/momentum/{match_id}")
async def get_momentum_analysis(
    match_id: str = Path(..., description="Match ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get momentum analysis for a match
    """
    logger.info("Fetching momentum analysis", match_id=match_id)

    # Verify match exists
    match_service = MatchService(db)
    match = await match_service.get_match(match_id)
    if not match:
        raise MatchNotFoundException(match_id)

    analytics_service = AnalyticsService(db)
    momentum = await analytics_service.get_momentum_analysis(match_id)

    return momentum


@router.get("/court-coverage/{match_id}")
async def get_court_coverage(
    match_id: str = Path(..., description="Match ID"),
    player_id: Optional[str] = Query(None, description="Specific player ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get court coverage analysis for a match
    """
    logger.info("Fetching court coverage analysis", match_id=match_id, player_id=player_id)

    # Verify match exists
    match_service = MatchService(db)
    match = await match_service.get_match(match_id)
    if not match:
        raise MatchNotFoundException(match_id)

    analytics_service = AnalyticsService(db)
    coverage = await analytics_service.get_court_coverage_analysis(match_id, player_id)

    return coverage


@router.get("/performance-forecast/{player_id}")
async def get_performance_forecast(
    player_id: str = Path(..., description="Player ID"),
    opponent_id: Optional[str] = Query(None, description="Opponent ID for head-to-head forecast"),
    surface: Optional[str] = Query(None, description="Court surface for forecast"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered performance forecast for a player
    """
    logger.info("Generating performance forecast", player_id=player_id, opponent_id=opponent_id)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    if opponent_id:
        opponent = await player_service.get_player(opponent_id)
        if not opponent:
            raise PlayerNotFoundException(opponent_id)

    analytics_service = AnalyticsService(db)
    forecast = await analytics_service.generate_performance_forecast(
        player_id, opponent_id, surface
    )

    return forecast