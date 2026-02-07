"""
Point history service for detailed point tracking and analysis
"""

from typing import Optional, List, Dict
from datetime import datetime
import uuid

from sqlalchemy import select, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.point_history import (
    PointDetails,
    PointHistoryFilter,
    PointHistorySummary,
    PointOutcome,
    PointHistory as PointHistoryORM,
)


class PointHistoryService:
    """
    Service for managing detailed point history
    Provides methods to:
    - Record detailed point information
    - Query points by various filters
    - Get break points for critical moment analysis
    - Generate statistics and summaries
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_point(self, point: PointDetails) -> PointDetails:
        """
        Create a new point record

        Args:
            point: PointDetails object

        Returns:
            Created PointDetails
        """
        point_orm = PointHistoryORM(
            id=uuid.uuid4(),
            match_id=point.match_id,
            set_number=point.set_number,
            game_number=point.game_number,
            point_number=point.point_number,
            score_before=point.score_before,
            score_after=point.score_after,
            set_score_before=point.set_score_before if hasattr(point, 'set_score_before') else None,
            set_score_after=point.set_score_after if hasattr(point, 'set_score_after') else None,
            server_player_id=point.server_player_id,
            receiver_player_id=point.receiver_player_id,
            point_winner_id=point.point_winner_id,
            outcome=point.outcome.value,
            winning_shot=point.winning_shot,
            error_type=point.error_type,
            rally_length=point.rally_length,
            rally_duration=point.rally_duration,
            is_first_serve=point.is_first_serve,
            serve_speed=point.serve_speed,
            serve_placement=point.serve_placement,
            is_serve_in=point.is_serve_in,
            is_break_point=point.is_break_point,
            is_set_point=point.is_set_point,
            is_match_point=point.is_match_point,
            is_game_point=point.is_game_point,
            timestamp=point.timestamp,
            video_timestamp=point.video_timestamp,
            court_position_data=point.court_position_data,
            ball_trajectory_data=point.ball_trajectory_data,
            notes=point.notes,
        )

        self.db.add(point_orm)
        await self.db.flush()
        await self.db.refresh(point_orm)

        return point

    async def get_point(self, point_id: str) -> Optional[PointDetails]:
        """Get point by ID"""
        stmt = select(PointHistoryORM).where(PointHistoryORM.id == uuid.UUID(point_id))
        result = await self.db.execute(stmt)
        point_orm = result.scalar_one_or_none()

        if not point_orm:
            return None

        return self._orm_to_pydantic(point_orm)

    async def get_points_by_match(self, match_id: str) -> List[PointDetails]:
        """
        Get all points for a match

        Args:
            match_id: Match ID

        Returns:
            List of PointDetails ordered by occurrence
        """
        stmt = select(PointHistoryORM).where(
            PointHistoryORM.match_id == match_id
        ).order_by(
            PointHistoryORM.set_number,
            PointHistoryORM.game_number,
            PointHistoryORM.point_number
        )

        result = await self.db.execute(stmt)
        points = result.scalars().all()

        return [self._orm_to_pydantic(p) for p in points]

    async def get_points_by_player(
        self,
        match_id: str,
        player_id: str,
        won_only: bool = False
    ) -> List[PointDetails]:
        """
        Get points for a specific player

        Args:
            match_id: Match ID
            player_id: Player ID
            won_only: If True, only return points won by player

        Returns:
            List of PointDetails
        """
        stmt = select(PointHistoryORM).where(PointHistoryORM.match_id == match_id)

        if won_only:
            stmt = stmt.where(PointHistoryORM.point_winner_id == player_id)
        else:
            # Points where player was server or receiver
            stmt = stmt.where(
                or_(
                    PointHistoryORM.server_player_id == player_id,
                    PointHistoryORM.receiver_player_id == player_id
                )
            )

        stmt = stmt.order_by(
            PointHistoryORM.set_number,
            PointHistoryORM.game_number,
            PointHistoryORM.point_number
        )

        result = await self.db.execute(stmt)
        points = result.scalars().all()

        return [self._orm_to_pydantic(p) for p in points]

    async def get_points_by_set(self, match_id: str, set_number: int) -> List[PointDetails]:
        """
        Get points for a specific set

        Args:
            match_id: Match ID
            set_number: Set number (1-5)

        Returns:
            List of PointDetails
        """
        stmt = select(PointHistoryORM).where(
            and_(
                PointHistoryORM.match_id == match_id,
                PointHistoryORM.set_number == set_number
            )
        ).order_by(
            PointHistoryORM.game_number,
            PointHistoryORM.point_number
        )

        result = await self.db.execute(stmt)
        points = result.scalars().all()

        return [self._orm_to_pydantic(p) for p in points]

    async def get_break_points(self, match_id: str) -> List[PointDetails]:
        """
        Get all break points for analysis of critical moments

        Args:
            match_id: Match ID

        Returns:
            List of PointDetails for break points
        """
        stmt = select(PointHistoryORM).where(
            and_(
                PointHistoryORM.match_id == match_id,
                PointHistoryORM.is_break_point == True
            )
        ).order_by(
            PointHistoryORM.set_number,
            PointHistoryORM.game_number,
            PointHistoryORM.point_number
        )

        result = await self.db.execute(stmt)
        points = result.scalars().all()

        return [self._orm_to_pydantic(p) for p in points]

    async def get_points_by_outcome(
        self,
        match_id: str,
        outcome: PointOutcome
    ) -> List[PointDetails]:
        """
        Get points by outcome type

        Args:
            match_id: Match ID
            outcome: PointOutcome (ACE, WINNER, etc.)

        Returns:
            List of PointDetails
        """
        stmt = select(PointHistoryORM).where(
            and_(
                PointHistoryORM.match_id == match_id,
                PointHistoryORM.outcome == outcome.value
            )
        ).order_by(
            PointHistoryORM.set_number,
            PointHistoryORM.game_number,
            PointHistoryORM.point_number
        )

        result = await self.db.execute(stmt)
        points = result.scalars().all()

        return [self._orm_to_pydantic(p) for p in points]

    async def query_points(self, filter: PointHistoryFilter) -> List[PointDetails]:
        """
        Query points with complex filters

        Args:
            filter: PointHistoryFilter with optional criteria

        Returns:
            List of PointDetails matching filter
        """
        stmt = select(PointHistoryORM)

        conditions = []

        if filter.match_id:
            conditions.append(PointHistoryORM.match_id == filter.match_id)
        if filter.set_number:
            conditions.append(PointHistoryORM.set_number == filter.set_number)
        if filter.outcome:
            conditions.append(PointHistoryORM.outcome == filter.outcome.value)
        if filter.is_break_point is not None:
            conditions.append(PointHistoryORM.is_break_point == filter.is_break_point)
        if filter.is_set_point is not None:
            conditions.append(PointHistoryORM.is_set_point == filter.is_set_point)
        if filter.is_match_point is not None:
            conditions.append(PointHistoryORM.is_match_point == filter.is_match_point)

        # Rally length range
        if filter.min_rally_length is not None:
            conditions.append(PointHistoryORM.rally_length >= filter.min_rally_length)
        if filter.max_rally_length is not None:
            conditions.append(PointHistoryORM.rally_length <= filter.max_rally_length)

        # Player filter
        if filter.player_id:
            conditions.append(
                or_(
                    PointHistoryORM.server_player_id == filter.player_id,
                    PointHistoryORM.receiver_player_id == filter.player_id,
                    PointHistoryORM.point_winner_id == filter.player_id
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(
            PointHistoryORM.set_number,
            PointHistoryORM.game_number,
            PointHistoryORM.point_number
        )

        result = await self.db.execute(stmt)
        points = result.scalars().all()

        return [self._orm_to_pydantic(p) for p in points]

    async def get_match_summary(self, match_id: str) -> PointHistorySummary:
        """
        Get summary statistics for match

        Args:
            match_id: Match ID

        Returns:
            PointHistorySummary with aggregated stats
        """
        points = await self.get_points_by_match(match_id)

        if not points:
            return PointHistorySummary(
                total_points=0,
                points_by_outcome={},
                average_rally_length=0.0,
                break_points_total=0,
                break_points_converted=0,
                aces_count=0,
                double_faults_count=0,
                winners_count=0,
                unforced_errors_count=0
            )

        # Count by outcome
        points_by_outcome = {}
        for point in points:
            outcome = point.outcome
            points_by_outcome[outcome] = points_by_outcome.get(outcome, 0) + 1

        # Calculate averages
        total_rally_length = sum(p.rally_length for p in points)
        average_rally_length = total_rally_length / len(points) if points else 0.0

        # Break points
        break_points = [p for p in points if p.is_break_point]
        break_points_total = len(break_points)
        # Break point converted if server lost the point
        break_points_converted = sum(
            1 for p in break_points
            if p.point_winner_id != p.server_player_id
        )

        # Specific outcomes
        aces_count = points_by_outcome.get(PointOutcome.ACE, 0)
        double_faults_count = points_by_outcome.get(PointOutcome.DOUBLE_FAULT, 0)
        winners_count = sum(
            points_by_outcome.get(outcome, 0)
            for outcome in [
                PointOutcome.WINNER,
                PointOutcome.SERVICE_WINNER,
                PointOutcome.RETURN_WINNER,
                PointOutcome.VOLLEY_WINNER,
                PointOutcome.SMASH_WINNER,
                PointOutcome.DROP_SHOT_WINNER
            ]
        )
        unforced_errors_count = points_by_outcome.get(PointOutcome.UNFORCED_ERROR, 0)

        return PointHistorySummary(
            total_points=len(points),
            points_by_outcome=points_by_outcome,
            average_rally_length=average_rally_length,
            break_points_total=break_points_total,
            break_points_converted=break_points_converted,
            aces_count=aces_count,
            double_faults_count=double_faults_count,
            winners_count=winners_count,
            unforced_errors_count=unforced_errors_count
        )

    async def delete_match_points(self, match_id: str) -> int:
        """
        Delete all points for a match

        Args:
            match_id: Match ID

        Returns:
            Number of deleted points
        """
        stmt = delete(PointHistoryORM).where(PointHistoryORM.match_id == match_id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount

    def _orm_to_pydantic(self, point_orm: PointHistoryORM) -> PointDetails:
        """Convert ORM model to Pydantic model"""
        return PointDetails(
            point_id=str(point_orm.id),
            match_id=point_orm.match_id,
            set_number=point_orm.set_number,
            game_number=point_orm.game_number,
            point_number=point_orm.point_number,
            score_before=point_orm.score_before or {},
            score_after=point_orm.score_after or {},
            set_score_before=point_orm.set_score_before or {},
            set_score_after=point_orm.set_score_after or {},
            server_player_id=point_orm.server_player_id,
            receiver_player_id=point_orm.receiver_player_id,
            point_winner_id=point_orm.point_winner_id,
            outcome=PointOutcome(point_orm.outcome),
            winning_shot=point_orm.winning_shot,
            error_type=point_orm.error_type,
            rally_length=point_orm.rally_length,
            rally_duration=point_orm.rally_duration,
            is_first_serve=point_orm.is_first_serve,
            serve_speed=point_orm.serve_speed,
            serve_placement=point_orm.serve_placement,
            is_serve_in=point_orm.is_serve_in,
            is_break_point=point_orm.is_break_point,
            is_set_point=point_orm.is_set_point,
            is_match_point=point_orm.is_match_point,
            is_game_point=point_orm.is_game_point,
            timestamp=point_orm.timestamp,
            video_timestamp=point_orm.video_timestamp,
            court_position_data=point_orm.court_position_data,
            ball_trajectory_data=point_orm.ball_trajectory_data,
            notes=point_orm.notes,
        )
