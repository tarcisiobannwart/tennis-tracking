"""
Analytics service for performance analysis and statistics
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.models.match import Match
from app.models.player import Player
from app.models.point import Point
from app.models.event import Event
from app.schemas.analytics import (
    PerformanceAnalytics,
    HeatmapData,
    PlayerComparison,
    TrendAnalysis,
    MatchInsights,
    PerformanceMetrics,
    HeatmapPoint
)
from app.schemas.player import PlayerStats

logger = structlog.get_logger(__name__)


class AnalyticsService:
    """Service for analytics and performance analysis"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_match_statistics(self, match_id: str) -> Dict[str, Any]:
        """Get comprehensive match statistics"""

        # Get match
        match_query = select(Match).where(Match.id == match_id)
        match_result = await self.db.execute(match_query)
        match = match_result.scalar_one_or_none()

        if not match:
            return {}

        # Get points for the match
        points_query = select(Point).where(Point.match_id == match_id)
        points_result = await self.db.execute(points_query)
        points = points_result.scalars().all()

        # Calculate basic statistics
        total_points = len(points)
        player1_points = len([p for p in points if p.winner_player_id == match.player1_id])
        player2_points = len([p for p in points if p.winner_player_id == match.player2_id])

        # Calculate rally statistics
        rally_lengths = [p.rally_length for p in points if p.rally_length > 0]
        avg_rally_length = sum(rally_lengths) / len(rally_lengths) if rally_lengths else 0
        max_rally_length = max(rally_lengths) if rally_lengths else 0

        # Calculate serve statistics
        serves = [p for p in points if p.server_player_id]
        aces = len([p for p in points if p.outcome == "ace"])
        double_faults = len([p for p in points if p.outcome == "double_fault"])

        return {
            "match_id": match_id,
            "duration_minutes": match.duration_minutes,
            "total_points": total_points,
            "total_games": 0,  # TODO: Calculate from games table
            "total_sets": match.player1_sets + match.player2_sets,
            "player1_stats": {
                "points_won": player1_points,
                "points_total": total_points,
                "points_percentage": (player1_points / total_points * 100) if total_points > 0 else 0,
                "sets_won": match.player1_sets
            },
            "player2_stats": {
                "points_won": player2_points,
                "points_total": total_points,
                "points_percentage": (player2_points / total_points * 100) if total_points > 0 else 0,
                "sets_won": match.player2_sets
            },
            "rally_stats": {
                "average_length": avg_rally_length,
                "max_length": max_rally_length,
                "total_rallies": len(rally_lengths)
            },
            "serve_stats": {
                "total_serves": len(serves),
                "aces": aces,
                "double_faults": double_faults
            }
        }

    async def get_player_statistics(
        self,
        player_id: str,
        period: str = "all",
        surface: Optional[str] = None
    ) -> PlayerStats:
        """Get comprehensive player statistics"""

        # Base query for player matches
        matches_query = select(Match).where(
            or_(Match.player1_id == player_id, Match.player2_id == player_id)
        )

        # Apply filters
        if surface:
            matches_query = matches_query.where(Match.surface == surface)

        if period != "all":
            # Add time-based filtering
            cutoff_date = self._get_period_cutoff(period)
            matches_query = matches_query.where(Match.created_at >= cutoff_date)

        matches_result = await self.db.execute(matches_query)
        matches = matches_result.scalars().all()

        # Calculate statistics
        total_matches = len(matches)
        wins = 0
        losses = 0
        sets_won = 0
        sets_lost = 0

        for match in matches:
            if match.status == "completed":
                if match.player1_id == player_id:
                    player_sets = match.player1_sets
                    opponent_sets = match.player2_sets
                else:
                    player_sets = match.player2_sets
                    opponent_sets = match.player1_sets

                sets_won += player_sets
                sets_lost += opponent_sets

                if player_sets > opponent_sets:
                    wins += 1
                else:
                    losses += 1

        win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0

        # Get points statistics
        points_query = select(Point).join(Match).where(
            Match.id == Point.match_id,
            or_(Match.player1_id == player_id, Match.player2_id == player_id)
        )
        points_result = await self.db.execute(points_query)
        points = points_result.scalars().all()

        total_points = len(points)
        points_won = len([p for p in points if p.winner_player_id == player_id])
        points_lost = total_points - points_won

        # Serve statistics
        serves = [p for p in points if p.server_player_id == player_id]
        aces = len([p for p in points if p.server_player_id == player_id and p.outcome == "ace"])
        double_faults = len([p for p in points if p.server_player_id == player_id and p.outcome == "double_fault"])

        first_serves = [p for p in serves if not p.second_serve]
        first_serve_in = len([p for p in first_serves if p.first_serve_in])
        first_serve_percentage = (first_serve_in / len(first_serves) * 100) if first_serves else 0

        return PlayerStats(
            player_id=player_id,
            total_matches=total_matches,
            wins=wins,
            losses=losses,
            win_percentage=win_percentage,
            total_sets_played=sets_won + sets_lost,
            sets_won=sets_won,
            sets_lost=sets_lost,
            total_games_played=0,  # TODO: Calculate from games
            games_won=0,
            games_lost=0,
            total_points_played=total_points,
            points_won=points_won,
            points_lost=points_lost,
            aces=aces,
            double_faults=double_faults,
            first_serve_percentage=first_serve_percentage,
            first_serve_points_won=0.0,  # TODO: Calculate
            second_serve_points_won=0.0,
            break_points_saved=0.0,
            break_points_converted=0.0,
            winners=0,  # TODO: Calculate from events
            unforced_errors=0,
            forced_errors=0,
            average_rally_length=0.0,
            longest_rally=0,
            average_match_duration=None,
            recent_form=[]
        )

    async def get_match_performance_analytics(
        self,
        match_id: str,
        player_id: Optional[str] = None
    ) -> List[PerformanceAnalytics]:
        """Get performance analytics for a match"""

        # Get match
        match_query = select(Match).where(Match.id == match_id)
        match_result = await self.db.execute(match_query)
        match = match_result.scalar_one_or_none()

        if not match:
            return []

        analytics = []
        player_ids = [match.player1_id, match.player2_id]

        if player_id:
            player_ids = [player_id]

        for pid in player_ids:
            # Calculate performance metrics for this player
            metrics = await self._calculate_player_performance_metrics(match_id, pid)

            analytics.append(PerformanceAnalytics(
                match_id=match_id,
                player_id=pid,
                metrics=metrics,
                shot_analysis={},  # TODO: Implement
                movement_analysis={},
                tactical_analysis={},
                comparison_to_average={},
                strengths=[],
                weaknesses=[],
                recommendations=[]
            ))

        return analytics

    async def get_match_heatmap_data(
        self,
        match_id: str,
        player_id: Optional[str] = None,
        data_type: str = "position"
    ) -> List[HeatmapData]:
        """Get heatmap data for a match"""

        # Mock heatmap data - in real implementation, this would use
        # computer vision data from player positions and ball tracking
        heatmap_data = []

        if player_id:
            player_ids = [player_id]
        else:
            # Get both players
            match_query = select(Match).where(Match.id == match_id)
            match_result = await self.db.execute(match_query)
            match = match_result.scalar_one_or_none()
            if not match:
                return []
            player_ids = [match.player1_id, match.player2_id]

        for pid in player_ids:
            # Generate mock heatmap points
            points = []
            for i in range(50):  # Mock 50 data points
                points.append(HeatmapPoint(
                    x=0.2 + (i % 10) * 0.06,  # Mock court positions
                    y=0.1 + (i % 15) * 0.05,
                    intensity=0.1 + (i % 10) * 0.1,
                    count=1 + i % 5
                ))

            heatmap_data.append(HeatmapData(
                match_id=match_id,
                player_id=pid,
                data_type=data_type,
                points=points,
                court_dimensions={"width": 23.77, "length": 10.97},  # Tennis court dimensions
                metadata={"total_points": len(points)}
            ))

        return heatmap_data

    async def compare_players(
        self,
        player1_id: str,
        player2_id: str,
        period: str = "career",
        surface: Optional[str] = None
    ) -> PlayerComparison:
        """Compare two players' performance"""

        # Get statistics for both players
        player1_stats = await self.get_player_statistics(player1_id, period, surface)
        player2_stats = await self.get_player_statistics(player2_id, period, surface)

        # Calculate head-to-head record
        h2h = await self.get_head_to_head(player1_id, player2_id)

        # Create comparison metrics
        metrics_comparison = {
            "win_percentage": {
                "player1": player1_stats.win_percentage,
                "player2": player2_stats.win_percentage
            },
            "aces": {
                "player1": player1_stats.aces,
                "player2": player2_stats.aces
            },
            "double_faults": {
                "player1": player1_stats.double_faults,
                "player2": player2_stats.double_faults
            },
            "first_serve_percentage": {
                "player1": player1_stats.first_serve_percentage,
                "player2": player2_stats.first_serve_percentage
            }
        }

        return PlayerComparison(
            player1_id=player1_id,
            player2_id=player2_id,
            comparison_period=period,
            metrics_comparison=metrics_comparison,
            head_to_head=h2h,
            surface_performance={},  # TODO: Implement
            recent_form={},
            statistical_insights=[]
        )

    async def get_head_to_head(self, player1_id: str, player2_id: str) -> Dict[str, Any]:
        """Get head-to-head record between two players"""

        # Get matches between the two players
        h2h_query = select(Match).where(
            or_(
                and_(Match.player1_id == player1_id, Match.player2_id == player2_id),
                and_(Match.player1_id == player2_id, Match.player2_id == player1_id)
            ),
            Match.status == "completed"
        )

        h2h_result = await self.db.execute(h2h_query)
        matches = h2h_result.scalars().all()

        player1_wins = 0
        player2_wins = 0

        for match in matches:
            if match.player1_id == player1_id:
                if match.player1_sets > match.player2_sets:
                    player1_wins += 1
                else:
                    player2_wins += 1
            else:
                if match.player2_sets > match.player1_sets:
                    player1_wins += 1
                else:
                    player2_wins += 1

        total_matches = len(matches)

        return {
            "total_matches": total_matches,
            "player1_wins": player1_wins,
            "player2_wins": player2_wins,
            "player1_win_percentage": (player1_wins / total_matches * 100) if total_matches > 0 else 0
        }

    async def get_player_trends(
        self,
        player_id: str,
        metrics: List[str],
        period: str = "month"
    ) -> List[TrendAnalysis]:
        """Get trend analysis for a player"""

        trends = []

        for metric in metrics:
            # Mock trend data - in real implementation, this would calculate
            # historical data points for the specified metric
            trends.append(TrendAnalysis(
                player_id=player_id,
                metric=metric,
                period=period,
                data_points=[],  # TODO: Calculate historical data points
                trend_direction="improving",
                trend_strength=0.7,
                statistical_significance=True,
                insights=[f"Player showing improvement in {metric}"],
                predictions=None
            ))

        return trends

    async def generate_match_insights(self, match_id: str) -> MatchInsights:
        """Generate AI-powered insights for a match"""

        # Mock insights - in real implementation, this would use ML/AI
        return MatchInsights(
            match_id=match_id,
            key_moments=[],
            turning_points=[],
            momentum_shifts=[],
            tactical_patterns=[],
            performance_highlights=[],
            areas_for_improvement=[]
        )

    async def get_advanced_player_stats(
        self,
        player_id: str,
        period: str = "all",
        surface: Optional[str] = None,
        opponent_ranking: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get advanced statistics with additional filtering"""

        base_stats = await self.get_player_statistics(player_id, period, surface)

        # Add advanced metrics here
        return {
            "basic_stats": base_stats.dict(),
            "advanced_metrics": {
                "clutch_performance": {},  # TODO: Calculate clutch points performance
                "pressure_situations": {},  # TODO: Calculate performance under pressure
                "surface_breakdown": {},  # TODO: Performance by surface
                "opponent_ranking_breakdown": {}  # TODO: Performance vs different ranking levels
            }
        }

    def _calculate_player_performance_metrics(self, match_id: str, player_id: str) -> PerformanceMetrics:
        """Calculate performance metrics for a player in a match"""

        # Mock implementation - would calculate real metrics from match data
        return PerformanceMetrics(
            serve_percentage=65.0,
            ace_percentage=8.0,
            double_fault_percentage=3.0,
            first_serve_points_won=72.0,
            second_serve_points_won=55.0,
            break_points_saved=60.0,
            break_points_converted=40.0,
            winners=25,
            unforced_errors=18,
            forced_errors=12,
            net_points_won=75.0,
            baseline_points_won=68.0,
            average_rally_length=4.2,
            distance_covered=3500.0,
            average_speed=15.2,
            max_speed=28.5
        )

    def _get_period_cutoff(self, period: str) -> datetime:
        """Get cutoff date for period filtering"""

        now = datetime.utcnow()

        if period == "year":
            return now - timedelta(days=365)
        elif period == "month":
            return now - timedelta(days=30)
        elif period == "week":
            return now - timedelta(days=7)
        else:
            return datetime.min  # All time