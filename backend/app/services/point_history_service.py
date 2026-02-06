"""
Point history service for detailed point tracking and analysis
"""

from typing import Optional, List, Dict
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.point_history import (
    PointDetails,
    PointHistoryFilter,
    PointHistorySummary,
    PointOutcome
)
from app.core.mongodb import get_database


class PointHistoryService:
    """
    Service for managing detailed point history
    Provides methods to:
    - Record detailed point information
    - Query points by various filters
    - Get break points for critical moment analysis
    - Generate statistics and summaries
    """

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db or get_database()
        self.collection = self.db.get_collection("point_history")

    async def create_point(self, point: PointDetails) -> PointDetails:
        """
        Create a new point record

        Args:
            point: PointDetails object

        Returns:
            Created PointDetails
        """
        point_dict = point.model_dump()
        await self.collection.insert_one(point_dict)
        return point

    async def get_point(self, point_id: str) -> Optional[PointDetails]:
        """Get point by ID"""
        point_data = await self.collection.find_one({"point_id": point_id})
        if not point_data:
            return None

        point_data.pop("_id", None)
        return PointDetails(**point_data)

    async def get_points_by_match(self, match_id: str) -> List[PointDetails]:
        """
        Get all points for a match

        Args:
            match_id: Match ID

        Returns:
            List of PointDetails ordered by occurrence
        """
        cursor = self.collection.find({"match_id": match_id}).sort([
            ("set_number", 1),
            ("game_number", 1),
            ("point_number", 1)
        ])

        points = []
        async for point_data in cursor:
            point_data.pop("_id", None)
            points.append(PointDetails(**point_data))

        return points

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
        query = {"match_id": match_id}

        if won_only:
            query["point_winner_id"] = player_id
        else:
            # Points where player was server or receiver
            query["$or"] = [
                {"server_player_id": player_id},
                {"receiver_player_id": player_id}
            ]

        cursor = self.collection.find(query).sort([
            ("set_number", 1),
            ("game_number", 1),
            ("point_number", 1)
        ])

        points = []
        async for point_data in cursor:
            point_data.pop("_id", None)
            points.append(PointDetails(**point_data))

        return points

    async def get_points_by_set(self, match_id: str, set_number: int) -> List[PointDetails]:
        """
        Get points for a specific set

        Args:
            match_id: Match ID
            set_number: Set number (1-5)

        Returns:
            List of PointDetails
        """
        cursor = self.collection.find({
            "match_id": match_id,
            "set_number": set_number
        }).sort([
            ("game_number", 1),
            ("point_number", 1)
        ])

        points = []
        async for point_data in cursor:
            point_data.pop("_id", None)
            points.append(PointDetails(**point_data))

        return points

    async def get_break_points(self, match_id: str) -> List[PointDetails]:
        """
        Get all break points for analysis of critical moments

        Args:
            match_id: Match ID

        Returns:
            List of PointDetails for break points
        """
        cursor = self.collection.find({
            "match_id": match_id,
            "is_break_point": True
        }).sort([
            ("set_number", 1),
            ("game_number", 1),
            ("point_number", 1)
        ])

        points = []
        async for point_data in cursor:
            point_data.pop("_id", None)
            points.append(PointDetails(**point_data))

        return points

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
        cursor = self.collection.find({
            "match_id": match_id,
            "outcome": outcome.value
        }).sort([
            ("set_number", 1),
            ("game_number", 1),
            ("point_number", 1)
        ])

        points = []
        async for point_data in cursor:
            point_data.pop("_id", None)
            points.append(PointDetails(**point_data))

        return points

    async def query_points(self, filter: PointHistoryFilter) -> List[PointDetails]:
        """
        Query points with complex filters

        Args:
            filter: PointHistoryFilter with optional criteria

        Returns:
            List of PointDetails matching filter
        """
        query = {}

        if filter.match_id:
            query["match_id"] = filter.match_id
        if filter.set_number:
            query["set_number"] = filter.set_number
        if filter.outcome:
            query["outcome"] = filter.outcome.value
        if filter.is_break_point is not None:
            query["is_break_point"] = filter.is_break_point
        if filter.is_set_point is not None:
            query["is_set_point"] = filter.is_set_point
        if filter.is_match_point is not None:
            query["is_match_point"] = filter.is_match_point

        # Rally length range
        if filter.min_rally_length is not None or filter.max_rally_length is not None:
            query["rally_length"] = {}
            if filter.min_rally_length is not None:
                query["rally_length"]["$gte"] = filter.min_rally_length
            if filter.max_rally_length is not None:
                query["rally_length"]["$lte"] = filter.max_rally_length

        # Player filter
        if filter.player_id:
            query["$or"] = [
                {"server_player_id": filter.player_id},
                {"receiver_player_id": filter.player_id},
                {"point_winner_id": filter.player_id}
            ]

        cursor = self.collection.find(query).sort([
            ("set_number", 1),
            ("game_number", 1),
            ("point_number", 1)
        ])

        points = []
        async for point_data in cursor:
            point_data.pop("_id", None)
            points.append(PointDetails(**point_data))

        return points

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
        result = await self.collection.delete_many({"match_id": match_id})
        return result.deleted_count
