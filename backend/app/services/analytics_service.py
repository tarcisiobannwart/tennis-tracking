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
        """Get head-to-head record between two players with detailed history"""

        # Get matches between the two players ordered by date
        h2h_query = select(Match).where(
            or_(
                and_(Match.player1_id == player1_id, Match.player2_id == player2_id),
                and_(Match.player1_id == player2_id, Match.player2_id == player1_id)
            ),
            Match.status == "completed"
        ).order_by(desc(Match.created_at))

        h2h_result = await self.db.execute(h2h_query)
        matches = h2h_result.scalars().all()

        player1_wins = 0
        player2_wins = 0
        surface_breakdown = {}
        match_history = []

        for match in matches:
            # Determine winner
            if match.player1_id == player1_id:
                player1_won = match.player1_sets > match.player2_sets
                player1_sets = match.player1_sets
                player2_sets = match.player2_sets
            else:
                player1_won = match.player2_sets > match.player1_sets
                player1_sets = match.player2_sets
                player2_sets = match.player1_sets

            if player1_won:
                player1_wins += 1
                winner_id = player1_id
            else:
                player2_wins += 1
                winner_id = player2_id

            # Track surface breakdown
            surface = match.surface or "unknown"
            if surface not in surface_breakdown:
                surface_breakdown[surface] = {"player1_wins": 0, "player2_wins": 0, "total": 0}

            if player1_won:
                surface_breakdown[surface]["player1_wins"] += 1
            else:
                surface_breakdown[surface]["player2_wins"] += 1
            surface_breakdown[surface]["total"] += 1

            # Add to match history
            match_history.append({
                "match_id": match.id,
                "date": match.created_at.isoformat() if match.created_at else None,
                "winner_id": winner_id,
                "score": f"{player1_sets}-{player2_sets}",
                "surface": surface,
                "tournament": getattr(match, "tournament_name", None),
                "duration_minutes": match.duration_minutes
            })

        total_matches = len(matches)
        player1_win_pct = (player1_wins / total_matches * 100) if total_matches > 0 else 0
        player2_win_pct = (player2_wins / total_matches * 100) if total_matches > 0 else 0

        # Recent form (last 5 matches)
        recent_form = []
        for match_info in match_history[:5]:
            if match_info["winner_id"] == player1_id:
                recent_form.append("W1")  # Player 1 won
            else:
                recent_form.append("W2")  # Player 2 won

        return {
            "player1_id": player1_id,
            "player2_id": player2_id,
            "total_matches": total_matches,
            "player1_wins": player1_wins,
            "player2_wins": player2_wins,
            "player1_win_percentage": player1_win_pct,
            "player2_win_percentage": player2_win_pct,
            "surface_breakdown": surface_breakdown,
            "recent_form": recent_form,
            "match_history": match_history
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

    async def get_rally_analysis(
        self,
        match_id: str,
        min_length: int = 3,
        max_length: Optional[int] = None,
        rally_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed rally analysis for a match"""

        # Get points for the match
        points_query = select(Point).where(Point.match_id == match_id)
        points_result = await self.db.execute(points_query)
        points = points_result.scalars().all()

        # Filter rallies by length
        rallies = [p for p in points if p.rally_length >= min_length]
        if max_length:
            rallies = [p for p in rallies if p.rally_length <= max_length]

        # Calculate rally statistics
        total_rallies = len(rallies)
        rally_lengths = [p.rally_length for p in rallies]
        avg_rally_length = sum(rally_lengths) / len(rally_lengths) if rally_lengths else 0
        max_rally = max(rally_lengths) if rally_lengths else 0

        # Distribution by duration
        distribution = {
            "short (3-5)": len([r for r in rally_lengths if 3 <= r <= 5]),
            "medium (6-9)": len([r for r in rally_lengths if 6 <= r <= 9]),
            "long (10-15)": len([r for r in rally_lengths if 10 <= r <= 15]),
            "very_long (16+)": len([r for r in rally_lengths if r >= 16])
        }

        # Winners by rally length
        winner_breakdown = {}
        for rally in rallies:
            winner_id = rally.winner_player_id
            if winner_id not in winner_breakdown:
                winner_breakdown[winner_id] = {
                    "total": 0,
                    "short": 0,
                    "medium": 0,
                    "long": 0,
                    "very_long": 0
                }

            winner_breakdown[winner_id]["total"] += 1
            if rally.rally_length <= 5:
                winner_breakdown[winner_id]["short"] += 1
            elif rally.rally_length <= 9:
                winner_breakdown[winner_id]["medium"] += 1
            elif rally.rally_length <= 15:
                winner_breakdown[winner_id]["long"] += 1
            else:
                winner_breakdown[winner_id]["very_long"] += 1

        # Outcome types
        outcome_types = {}
        for rally in rallies:
            outcome = rally.outcome or "unknown"
            outcome_types[outcome] = outcome_types.get(outcome, 0) + 1

        return {
            "match_id": match_id,
            "total_rallies": total_rallies,
            "average_rally_length": round(avg_rally_length, 2),
            "max_rally_length": max_rally,
            "distribution_by_duration": distribution,
            "winner_breakdown": winner_breakdown,
            "outcome_types": outcome_types,
            "filters": {
                "min_length": min_length,
                "max_length": max_length,
                "rally_type": rally_type
            }
        }

    async def get_serve_analysis(
        self,
        match_id: str,
        player_id: Optional[str] = None,
        serve_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed serve analysis for a match"""

        # Get points for the match
        points_query = select(Point).where(Point.match_id == match_id)
        points_result = await self.db.execute(points_query)
        points = points_result.scalars().all()

        # Get match to identify players
        match_query = select(Match).where(Match.id == match_id)
        match_result = await self.db.execute(match_query)
        match = match_result.scalar_one_or_none()

        if not match:
            return {}

        player_ids = [match.player1_id, match.player2_id]
        if player_id:
            player_ids = [player_id]

        serve_stats = {}

        for pid in player_ids:
            # Filter serves by this player
            serves = [p for p in points if p.server_player_id == pid]

            if serve_type == "first":
                serves = [s for s in serves if not s.second_serve]
            elif serve_type == "second":
                serves = [s for s in serves if s.second_serve]

            total_serves = len(serves)
            first_serves = [s for s in serves if not s.second_serve]
            second_serves = [s for s in serves if s.second_serve]

            # First serve stats
            first_serve_in = len([s for s in first_serves if s.first_serve_in])
            first_serve_pct = (first_serve_in / len(first_serves) * 100) if first_serves else 0

            first_serve_won = len([s for s in first_serves if s.first_serve_in and s.winner_player_id == pid])
            first_serve_won_pct = (first_serve_won / first_serve_in * 100) if first_serve_in > 0 else 0

            # Second serve stats
            second_serve_won = len([s for s in second_serves if s.winner_player_id == pid])
            second_serve_won_pct = (second_serve_won / len(second_serves) * 100) if second_serves else 0

            # Aces and double faults
            aces = len([s for s in serves if s.outcome == "ace"])
            double_faults = len([s for s in serves if s.outcome == "double_fault"])

            # Serve direction (if available)
            serve_directions = {}
            for serve in serves:
                direction = getattr(serve, "serve_direction", None) or "center"
                serve_directions[direction] = serve_directions.get(direction, 0) + 1

            # Serve speed (if available - mock data for now)
            avg_first_serve_speed = 180.0  # km/h - would be calculated from actual data
            avg_second_serve_speed = 150.0  # km/h

            serve_stats[pid] = {
                "player_id": pid,
                "total_serves": total_serves,
                "first_serves": {
                    "total": len(first_serves),
                    "in": first_serve_in,
                    "percentage": round(first_serve_pct, 2),
                    "won": first_serve_won,
                    "won_percentage": round(first_serve_won_pct, 2),
                    "average_speed_kmh": avg_first_serve_speed
                },
                "second_serves": {
                    "total": len(second_serves),
                    "won": second_serve_won,
                    "won_percentage": round(second_serve_won_pct, 2),
                    "average_speed_kmh": avg_second_serve_speed
                },
                "aces": aces,
                "double_faults": double_faults,
                "serve_direction_distribution": serve_directions
            }

        return {
            "match_id": match_id,
            "serve_statistics": serve_stats,
            "filters": {
                "player_id": player_id,
                "serve_type": serve_type
            }
        }

    async def get_momentum_analysis(self, match_id: str) -> Dict[str, Any]:
        """Get momentum analysis for a match"""

        # Get match
        match_query = select(Match).where(Match.id == match_id)
        match_result = await self.db.execute(match_query)
        match = match_result.scalar_one_or_none()

        if not match:
            return {}

        # Get points for the match ordered by time
        points_query = select(Point).where(Point.match_id == match_id).order_by(Point.created_at)
        points_result = await self.db.execute(points_query)
        points = points_result.scalars().all()

        player1_id = match.player1_id
        player2_id = match.player2_id

        # Calculate momentum over time
        momentum_timeline = []
        player1_streak = 0
        player2_streak = 0
        player1_points_total = 0
        player2_points_total = 0
        turning_points = []

        for i, point in enumerate(points):
            # Update point totals
            if point.winner_player_id == player1_id:
                player1_points_total += 1
                player1_streak += 1
                player2_streak = 0
            elif point.winner_player_id == player2_id:
                player2_points_total += 1
                player2_streak += 1
                player1_streak = 0

            # Calculate momentum score (-100 to +100, positive = player1 advantage)
            total_points = player1_points_total + player2_points_total
            if total_points > 0:
                momentum_score = ((player1_points_total - player2_points_total) / total_points) * 100
            else:
                momentum_score = 0

            # Detect turning points (momentum swing > 20 points)
            if len(momentum_timeline) > 0:
                prev_momentum = momentum_timeline[-1]["momentum_score"]
                momentum_change = abs(momentum_score - prev_momentum)
                if momentum_change > 20:
                    turning_points.append({
                        "point_index": i,
                        "point_id": point.id,
                        "momentum_before": prev_momentum,
                        "momentum_after": momentum_score,
                        "change": momentum_change,
                        "set_number": getattr(point, "set_number", None),
                        "game_number": getattr(point, "game_number", None)
                    })

            momentum_timeline.append({
                "point_index": i,
                "point_id": point.id,
                "momentum_score": round(momentum_score, 2),
                "player1_points": player1_points_total,
                "player2_points": player2_points_total,
                "player1_streak": player1_streak,
                "player2_streak": player2_streak,
                "timestamp": point.created_at.isoformat() if point.created_at else None
            })

        # Calculate momentum phases
        player1_dominant_phases = len([m for m in momentum_timeline if m["momentum_score"] > 30])
        player2_dominant_phases = len([m for m in momentum_timeline if m["momentum_score"] < -30])
        balanced_phases = len([m for m in momentum_timeline if -30 <= m["momentum_score"] <= 30])

        return {
            "match_id": match_id,
            "player1_id": player1_id,
            "player2_id": player2_id,
            "momentum_timeline": momentum_timeline,
            "turning_points": turning_points,
            "momentum_phases": {
                "player1_dominant": player1_dominant_phases,
                "player2_dominant": player2_dominant_phases,
                "balanced": balanced_phases
            },
            "final_momentum": momentum_timeline[-1]["momentum_score"] if momentum_timeline else 0,
            "max_player1_momentum": max([m["momentum_score"] for m in momentum_timeline]) if momentum_timeline else 0,
            "max_player2_momentum": min([m["momentum_score"] for m in momentum_timeline]) if momentum_timeline else 0
        }

    async def get_court_coverage_analysis(
        self,
        match_id: str,
        player_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get court coverage analysis for a match"""

        # Get match
        match_query = select(Match).where(Match.id == match_id)
        match_result = await self.db.execute(match_query)
        match = match_result.scalar_one_or_none()

        if not match:
            return {}

        # Get events (player positions) for the match
        events_query = select(Event).where(Event.match_id == match_id)
        events_result = await self.db.execute(events_query)
        events = events_result.scalars().all()

        player_ids = [match.player1_id, match.player2_id]
        if player_id:
            player_ids = [player_id]

        coverage_stats = {}

        for pid in player_ids:
            # Filter events for this player
            player_events = [e for e in events if e.player_id == pid and e.event_type == "position"]

            # Calculate distance covered (sum of distances between consecutive positions)
            total_distance = 0.0
            positions = []

            for i, event in enumerate(player_events):
                x = getattr(event, "position_x", 0.0)
                y = getattr(event, "position_y", 0.0)
                positions.append({"x": x, "y": y})

                if i > 0:
                    prev_x = getattr(player_events[i-1], "position_x", 0.0)
                    prev_y = getattr(player_events[i-1], "position_y", 0.0)
                    distance = ((x - prev_x)**2 + (y - prev_y)**2)**0.5
                    total_distance += distance

            # Calculate area covered (convex hull approximation)
            # For simplicity, calculate bounding box area
            if positions:
                x_coords = [p["x"] for p in positions]
                y_coords = [p["y"] for p in positions]
                area_covered = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
            else:
                area_covered = 0.0

            # Zone frequency (divide court into 9 zones)
            zones = {
                "left_baseline": 0,
                "center_baseline": 0,
                "right_baseline": 0,
                "left_mid": 0,
                "center_mid": 0,
                "right_mid": 0,
                "left_net": 0,
                "center_net": 0,
                "right_net": 0
            }

            for pos in positions:
                x, y = pos["x"], pos["y"]
                # Assuming court dimensions: x (0-23.77m), y (0-10.97m)
                # Left/Center/Right based on y
                if y < 3.66:
                    horizontal = "left"
                elif y < 7.31:
                    horizontal = "center"
                else:
                    horizontal = "right"

                # Baseline/Mid/Net based on x
                if x < 7.92:
                    vertical = "baseline"
                elif x < 15.85:
                    vertical = "mid"
                else:
                    vertical = "net"

                zone_key = f"{horizontal}_{vertical}"
                if zone_key in zones:
                    zones[zone_key] += 1

            # Most frequented zone
            most_frequented_zone = max(zones, key=zones.get) if zones else None

            coverage_stats[pid] = {
                "player_id": pid,
                "total_distance_meters": round(total_distance, 2),
                "area_covered_sqm": round(area_covered, 2),
                "total_positions_tracked": len(positions),
                "zone_frequency": zones,
                "most_frequented_zone": most_frequented_zone,
                "average_position": {
                    "x": sum(p["x"] for p in positions) / len(positions) if positions else 0,
                    "y": sum(p["y"] for p in positions) / len(positions) if positions else 0
                }
            }

        return {
            "match_id": match_id,
            "court_coverage": coverage_stats,
            "court_dimensions": {
                "length_meters": 23.77,
                "width_meters": 10.97
            }
        }

    async def get_movement_analysis(
        self,
        match_id: str,
        player_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed movement analysis for a match

        Returns:
        - average_speed: Average movement speed (m/s)
        - max_speed: Maximum speed reached (m/s)
        - total_distance: Total distance covered (meters)
        - sprints: Number of sprint bursts (speed > threshold)
        - time_in_zones: Time spent in each court zone
        - agility_score: Overall agility score (0-100)
        """

        # Get match
        match_query = select(Match).where(Match.id == match_id)
        match_result = await self.db.execute(match_query)
        match = match_result.scalar_one_or_none()

        if not match:
            return {}

        # Get events (player positions) for the match
        events_query = select(Event).where(
            Event.match_id == match_id,
            Event.event_type == "position"
        ).order_by(Event.created_at)
        events_result = await self.db.execute(events_query)
        events = events_result.scalars().all()

        player_ids = [match.player1_id, match.player2_id]
        if player_id:
            player_ids = [player_id]

        movement_stats = {}

        for pid in player_ids:
            # Filter events for this player
            player_events = [e for e in events if e.player_id == pid]

            if not player_events:
                movement_stats[pid] = {
                    "player_id": pid,
                    "average_speed_ms": 0.0,
                    "max_speed_ms": 0.0,
                    "total_distance_meters": 0.0,
                    "sprints": 0,
                    "time_in_zones": {},
                    "agility_score": 0.0,
                    "positions_tracked": 0
                }
                continue

            # Calculate distances and speeds
            total_distance = 0.0
            speeds = []
            sprint_threshold = 5.0  # m/s
            sprints = 0

            for i in range(1, len(player_events)):
                prev_event = player_events[i-1]
                curr_event = player_events[i]

                # Calculate distance
                prev_x = getattr(prev_event, "position_x", 0.0)
                prev_y = getattr(prev_event, "position_y", 0.0)
                curr_x = getattr(curr_event, "position_x", 0.0)
                curr_y = getattr(curr_event, "position_y", 0.0)

                distance = ((curr_x - prev_x)**2 + (curr_y - prev_y)**2)**0.5
                total_distance += distance

                # Calculate speed (distance / time)
                if prev_event.created_at and curr_event.created_at:
                    time_diff = (curr_event.created_at - prev_event.created_at).total_seconds()
                    if time_diff > 0:
                        speed = distance / time_diff
                        speeds.append(speed)

                        # Count sprints
                        if speed > sprint_threshold:
                            sprints += 1

            # Average and max speed
            average_speed = sum(speeds) / len(speeds) if speeds else 0.0
            max_speed = max(speeds) if speeds else 0.0

            # Time in zones (9 zones: left/center/right x baseline/mid/net)
            zone_times = {
                "left_baseline": 0,
                "center_baseline": 0,
                "right_baseline": 0,
                "left_mid": 0,
                "center_mid": 0,
                "right_mid": 0,
                "left_net": 0,
                "center_net": 0,
                "right_net": 0
            }

            for i, event in enumerate(player_events):
                x = getattr(event, "position_x", 0.0)
                y = getattr(event, "position_y", 0.0)

                # Determine zone (assuming court dimensions: x (0-23.77m), y (0-10.97m))
                if y < 3.66:
                    horizontal = "left"
                elif y < 7.31:
                    horizontal = "center"
                else:
                    horizontal = "right"

                if x < 7.92:
                    vertical = "baseline"
                elif x < 15.85:
                    vertical = "mid"
                else:
                    vertical = "net"

                zone_key = f"{horizontal}_{vertical}"
                if zone_key in zone_times:
                    # Approximate time in zone (time to next position)
                    if i < len(player_events) - 1 and event.created_at and player_events[i+1].created_at:
                        time_in_zone = (player_events[i+1].created_at - event.created_at).total_seconds()
                        zone_times[zone_key] += time_in_zone
                    else:
                        zone_times[zone_key] += 1  # Default 1 second

            # Agility score (0-100)
            # Based on: average speed, coverage area, sprint frequency
            speed_component = min(average_speed / 10.0, 1.0)  # Normalize to 0-1
            sprint_component = min(sprints / 50.0, 1.0)  # Normalize based on 50 sprints
            coverage_component = min(total_distance / 3000.0, 1.0)  # Normalize based on 3000m

            agility_score = (speed_component * 40 + sprint_component * 30 + coverage_component * 30) * 100

            movement_stats[pid] = {
                "player_id": pid,
                "average_speed_ms": round(average_speed, 2),
                "max_speed_ms": round(max_speed, 2),
                "total_distance_meters": round(total_distance, 2),
                "sprints": sprints,
                "time_in_zones": {k: round(v, 2) for k, v in zone_times.items()},
                "agility_score": round(agility_score, 2),
                "positions_tracked": len(player_events)
            }

        return {
            "match_id": match_id,
            "movement_analysis": movement_stats,
            "sprint_threshold_ms": sprint_threshold,
            "court_dimensions": {
                "length_meters": 23.77,
                "width_meters": 10.97
            }
        }

    async def get_player_efficiency(
        self,
        player_id: str,
        match_id: Optional[str] = None,
        period: str = "all"
    ) -> Dict[str, Any]:
        """
        Calculate player efficiency and consistency metrics

        Returns:
        - first_serve_pct: Percentage of first serves in
        - second_serve_pct: Percentage of second serves won
        - return_win_pct: Percentage of return points won
        - break_conversion: Break points converted percentage
        - consistency_score: Overall consistency (0-100)
        - unforced_error_ratio: Ratio of unforced errors to total points
        """

        # Base query for player points
        points_query = select(Point).join(Match).where(
            Match.id == Point.match_id,
            or_(Match.player1_id == player_id, Match.player2_id == player_id)
        )

        # Filter by specific match if provided
        if match_id:
            points_query = points_query.where(Match.id == match_id)
        elif period != "all":
            cutoff_date = self._get_period_cutoff(period)
            points_query = points_query.where(Match.created_at >= cutoff_date)

        points_result = await self.db.execute(points_query)
        points = points_result.scalars().all()

        if not points:
            return {
                "player_id": player_id,
                "first_serve_pct": 0.0,
                "second_serve_pct": 0.0,
                "return_win_pct": 0.0,
                "break_conversion": 0.0,
                "consistency_score": 0.0,
                "unforced_error_ratio": 0.0
            }

        # First serve statistics
        first_serves = [p for p in points if p.server_player_id == player_id and not p.second_serve]
        first_serve_in = len([s for s in first_serves if s.first_serve_in])
        first_serve_pct = (first_serve_in / len(first_serves) * 100) if first_serves else 0.0

        # Second serve statistics
        second_serves = [p for p in points if p.server_player_id == player_id and p.second_serve]
        second_serve_won = len([s for s in second_serves if s.winner_player_id == player_id])
        second_serve_pct = (second_serve_won / len(second_serves) * 100) if second_serves else 0.0

        # Return statistics (points where opponent served)
        return_points = [p for p in points if p.server_player_id != player_id and p.server_player_id is not None]
        return_won = len([p for p in return_points if p.winner_player_id == player_id])
        return_win_pct = (return_won / len(return_points) * 100) if return_points else 0.0

        # Break point conversion (mock for now - would need break point tracking)
        break_points_faced = len([p for p in points if getattr(p, "is_break_point", False)])
        break_points_converted = len([
            p for p in points
            if getattr(p, "is_break_point", False) and p.winner_player_id == player_id
        ])
        break_conversion = (break_points_converted / break_points_faced * 100) if break_points_faced > 0 else 0.0

        # Unforced errors ratio
        total_points = len(points)
        unforced_errors = len([
            p for p in points
            if p.outcome == "unforced_error" and getattr(p, "error_player_id", None) == player_id
        ])
        unforced_error_ratio = (unforced_errors / total_points) if total_points > 0 else 0.0

        # Consistency score (0-100)
        # Based on: low unforced errors, high first serve %, stable performance
        error_component = max(0, 1 - (unforced_error_ratio * 2))  # Lower errors = higher score
        serve_component = first_serve_pct / 100
        return_component = return_win_pct / 100

        consistency_score = (error_component * 40 + serve_component * 30 + return_component * 30) * 100

        return {
            "player_id": player_id,
            "match_id": match_id,
            "period": period,
            "first_serve_pct": round(first_serve_pct, 2),
            "second_serve_pct": round(second_serve_pct, 2),
            "return_win_pct": round(return_win_pct, 2),
            "break_conversion": round(break_conversion, 2),
            "consistency_score": round(consistency_score, 2),
            "unforced_error_ratio": round(unforced_error_ratio, 4),
            "total_points_analyzed": total_points
        }

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