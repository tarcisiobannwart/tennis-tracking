"""
Ranking service for business logic operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog

from app.models.ranking import (
    Ranking,
    RankingParticipant,
    RankingRound,
    RankingMatch,
    RankingType,
    RankingStatus,
)
from app.models.sql import User
from app.schemas.ranking import (
    RankingCreate,
    RankingUpdate,
    RankingParticipantCreate,
    RankingRoundCreate,
    RankingRoundUpdate,
    RankingMatchCreate,
    RankingMatchUpdate,
    StandingsEntry,
    StandingsResponse,
)

logger = structlog.get_logger(__name__)


class RankingService:
    """Service for ranking-related operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rankings(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        ranking_type: Optional[str] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> tuple[List[Ranking], int]:
        """Get rankings with optional filtering"""

        query = select(Ranking).order_by(desc(Ranking.created_at))

        # Apply filters
        conditions = []

        if status:
            conditions.append(Ranking.status == status)

        if ranking_type:
            conditions.append(Ranking.ranking_type == ranking_type)

        if organization_id:
            conditions.append(Ranking.organization_id == organization_id)

        if user_id:
            # Filter rankings where user is a participant
            subquery = select(RankingParticipant.ranking_id).where(
                RankingParticipant.user_id == user_id
            )
            conditions.append(Ranking.id.in_(subquery))

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        rankings = result.scalars().all()

        return list(rankings), total

    async def get_ranking(self, ranking_id: str) -> Optional[Ranking]:
        """Get a single ranking by ID"""

        query = select(Ranking).where(Ranking.id == ranking_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_ranking(self, ranking_data: RankingCreate, created_by: str) -> Ranking:
        """Create a new ranking"""

        ranking = Ranking(
            name=ranking_data.name,
            description=ranking_data.description,
            ranking_type=ranking_data.ranking_type,
            status=ranking_data.status,
            organization_id=ranking_data.organization_id,
            venue=ranking_data.venue,
            location=ranking_data.location,
            scoring_config=ranking_data.scoring_config or {
                "win_points": 3,
                "draw_points": 1,
                "loss_points": 0,
                "bonus_straight_sets": 1,
                "bonus_tiebreak": 0.5,
            },
            start_date=ranking_data.start_date,
            end_date=ranking_data.end_date,
            total_rounds=ranking_data.total_rounds,
            is_public=ranking_data.is_public,
            allow_self_scheduling=ranking_data.allow_self_scheduling,
            created_by=created_by,
        )

        self.db.add(ranking)
        await self.db.flush()
        await self.db.refresh(ranking)

        logger.info("ranking_created", ranking_id=ranking.id, name=ranking.name)
        return ranking

    async def update_ranking(
        self, ranking_id: str, ranking_data: RankingUpdate
    ) -> Optional[Ranking]:
        """Update a ranking"""

        ranking = await self.get_ranking(ranking_id)
        if not ranking:
            return None

        update_data = ranking_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ranking, field, value)

        await self.db.flush()
        await self.db.refresh(ranking)

        logger.info("ranking_updated", ranking_id=ranking.id)
        return ranking

    async def delete_ranking(self, ranking_id: str) -> bool:
        """Delete a ranking"""

        ranking = await self.get_ranking(ranking_id)
        if not ranking:
            return False

        await self.db.delete(ranking)
        await self.db.flush()

        logger.info("ranking_deleted", ranking_id=ranking_id)
        return True

    # Participant operations
    async def add_participant(
        self, participant_data: RankingParticipantCreate
    ) -> RankingParticipant:
        """Add a participant to a ranking"""

        participant = RankingParticipant(
            ranking_id=participant_data.ranking_id,
            user_id=participant_data.user_id,
        )

        self.db.add(participant)
        await self.db.flush()
        await self.db.refresh(participant)

        logger.info(
            "participant_added",
            ranking_id=participant.ranking_id,
            user_id=participant.user_id,
        )
        return participant

    async def get_participants(self, ranking_id: str) -> List[RankingParticipant]:
        """Get all participants in a ranking"""

        query = (
            select(RankingParticipant)
            .where(RankingParticipant.ranking_id == ranking_id)
            .order_by(RankingParticipant.position.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def remove_participant(self, participant_id: str) -> bool:
        """Remove a participant from a ranking"""

        query = select(RankingParticipant).where(RankingParticipant.id == participant_id)
        result = await self.db.execute(query)
        participant = result.scalar_one_or_none()

        if not participant:
            return False

        await self.db.delete(participant)
        await self.db.flush()

        logger.info("participant_removed", participant_id=participant_id)
        return True

    # Round operations
    async def get_rounds(self, ranking_id: str) -> List[RankingRound]:
        """Get all rounds in a ranking"""

        query = (
            select(RankingRound)
            .where(RankingRound.ranking_id == ranking_id)
            .order_by(RankingRound.round_number.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_round(self, round_id: str) -> Optional[RankingRound]:
        """Get a single round by ID"""

        query = select(RankingRound).where(RankingRound.id == round_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_round(self, round_data: RankingRoundCreate) -> RankingRound:
        """Create a new round in a ranking"""

        round_obj = RankingRound(
            ranking_id=round_data.ranking_id,
            round_number=round_data.round_number,
            name=round_data.name or f"Round {round_data.round_number}",
            start_date=round_data.start_date,
            end_date=round_data.end_date,
        )

        self.db.add(round_obj)
        await self.db.flush()
        await self.db.refresh(round_obj)

        logger.info("round_created", round_id=round_obj.id, ranking_id=round_obj.ranking_id)
        return round_obj

    async def update_round(
        self, round_id: str, round_data: RankingRoundUpdate
    ) -> Optional[RankingRound]:
        """Update a round"""

        round_obj = await self.get_round(round_id)
        if not round_obj:
            return None

        update_data = round_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(round_obj, field, value)

        await self.db.flush()
        await self.db.refresh(round_obj)

        logger.info("round_updated", round_id=round_id)
        return round_obj

    # Match operations
    async def get_matches(
        self, ranking_id: Optional[str] = None, round_id: Optional[str] = None
    ) -> List[RankingMatch]:
        """Get matches for a ranking or round"""

        query = select(RankingMatch)

        conditions = []
        if ranking_id:
            conditions.append(RankingMatch.ranking_id == ranking_id)
        if round_id:
            conditions.append(RankingMatch.round_id == round_id)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(RankingMatch.scheduled_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_match(self, match_id: str) -> Optional[RankingMatch]:
        """Get a single match by ID"""

        query = select(RankingMatch).where(RankingMatch.id == match_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_match(self, match_data: RankingMatchCreate) -> RankingMatch:
        """Create a new ranking match"""

        match = RankingMatch(
            ranking_id=match_data.ranking_id,
            round_id=match_data.round_id,
            player1_id=match_data.player1_id,
            player2_id=match_data.player2_id,
            scheduled_at=match_data.scheduled_at,
        )

        self.db.add(match)
        await self.db.flush()
        await self.db.refresh(match)

        logger.info("ranking_match_created", match_id=match.id, ranking_id=match.ranking_id)
        return match

    async def update_match(
        self, match_id: str, match_data: RankingMatchUpdate
    ) -> Optional[RankingMatch]:
        """Update a ranking match"""

        match = await self.get_match(match_id)
        if not match:
            return None

        update_data = match_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(match, field, value)

        await self.db.flush()
        await self.db.refresh(match)

        # If match is completed, update participant stats
        if match.status == "completed" and match.winner_id:
            await self._update_participant_stats_after_match(match)

        logger.info("ranking_match_updated", match_id=match_id)
        return match

    async def _update_participant_stats_after_match(self, match: RankingMatch) -> None:
        """Update participant statistics after a match is completed"""

        # Get participants
        p1_query = select(RankingParticipant).where(
            and_(
                RankingParticipant.ranking_id == match.ranking_id,
                RankingParticipant.user_id == match.player1_id,
            )
        )
        p2_query = select(RankingParticipant).where(
            and_(
                RankingParticipant.ranking_id == match.ranking_id,
                RankingParticipant.user_id == match.player2_id,
            )
        )

        p1_result = await self.db.execute(p1_query)
        p2_result = await self.db.execute(p2_query)

        participant1 = p1_result.scalar_one_or_none()
        participant2 = p2_result.scalar_one_or_none()

        if not participant1 or not participant2:
            return

        # Update match counts
        participant1.matches_played += 1
        participant2.matches_played += 1

        if match.winner_id == match.player1_id:
            participant1.matches_won += 1
            participant2.matches_lost += 1
        elif match.winner_id == match.player2_id:
            participant2.matches_won += 1
            participant1.matches_lost += 1
        else:
            # Draw
            participant1.matches_drawn += 1
            participant2.matches_drawn += 1

        # Update points
        participant1.points += match.player1_points
        participant2.points += match.player2_points

        await self.db.flush()

        # Recalculate standings
        await self._recalculate_standings(match.ranking_id)

    async def _recalculate_standings(self, ranking_id: str) -> None:
        """Recalculate standings and update positions"""

        query = (
            select(RankingParticipant)
            .where(RankingParticipant.ranking_id == ranking_id)
            .order_by(desc(RankingParticipant.points))
        )

        result = await self.db.execute(query)
        participants = list(result.scalars().all())

        for idx, participant in enumerate(participants, start=1):
            participant.previous_position = participant.position
            participant.position = idx

            # Update position history
            if participant.position_history is None:
                participant.position_history = []
            participant.position_history.append(participant.position)

        await self.db.flush()

    async def get_standings(self, ranking_id: str) -> StandingsResponse:
        """Get current standings for a ranking"""

        # Get ranking
        ranking = await self.get_ranking(ranking_id)
        if not ranking:
            raise ValueError("Ranking not found")

        # Get participants with user details
        query = (
            select(RankingParticipant, User)
            .join(User, RankingParticipant.user_id == User.id)
            .where(RankingParticipant.ranking_id == ranking_id)
            .order_by(RankingParticipant.position.asc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        standings = []
        for participant, user in rows:
            win_rate = (
                (participant.matches_won / participant.matches_played * 100)
                if participant.matches_played > 0
                else 0.0
            )
            set_ratio = (
                (participant.sets_won / participant.sets_lost)
                if participant.sets_lost > 0
                else float(participant.sets_won)
            )

            position_change = None
            if participant.previous_position and participant.position:
                position_change = participant.previous_position - participant.position

            standings.append(
                StandingsEntry(
                    position=participant.position or 0,
                    previous_position=participant.previous_position,
                    user_id=user.id,
                    user_name=user.full_name or user.email,
                    user_avatar=None,  # TODO: Add avatar support
                    points=participant.points,
                    matches_played=participant.matches_played,
                    matches_won=participant.matches_won,
                    matches_lost=participant.matches_lost,
                    matches_drawn=participant.matches_drawn,
                    sets_won=participant.sets_won,
                    sets_lost=participant.sets_lost,
                    games_won=participant.games_won,
                    games_lost=participant.games_lost,
                    win_rate=round(win_rate, 1),
                    set_ratio=round(set_ratio, 2),
                    position_history=participant.position_history or [],
                    position_change=position_change,
                )
            )

        return StandingsResponse(
            ranking_id=ranking_id,
            current_round=ranking.current_round,
            standings=standings,
            updated_at=datetime.utcnow(),
        )

    async def calculate_match_points(
        self, ranking_id: str, winner_id: str, loser_id: str, is_straight_sets: bool = False
    ) -> tuple[float, float]:
        """Calculate points for a completed match"""

        ranking = await self.get_ranking(ranking_id)
        if not ranking:
            raise ValueError("Ranking not found")

        config = ranking.scoring_config or {}
        win_points = config.get("win_points", 3)
        loss_points = config.get("loss_points", 0)
        bonus_straight_sets = config.get("bonus_straight_sets", 1)

        winner_points = win_points
        if is_straight_sets:
            winner_points += bonus_straight_sets

        return winner_points, loss_points
