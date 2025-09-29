"""
Match service for business logic operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import structlog

from app.models.match import Match, MatchStatus
from app.models.player import Player
from app.models.event import Event
from app.models.point import Point
from app.models.set import Set
from app.models.game import Game
from app.schemas.match import MatchCreate, MatchUpdate, MatchEventSummary

logger = structlog.get_logger(__name__)


class MatchService:
    """Service for match-related operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_matches(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        player_id: Optional[str] = None,
        tournament: Optional[str] = None
    ) -> List[Match]:
        """Get matches with optional filtering"""

        query = select(Match).order_by(desc(Match.created_at))

        # Apply filters
        conditions = []

        if status:
            conditions.append(Match.status == status)

        if player_id:
            conditions.append(
                or_(Match.player1_id == player_id, Match.player2_id == player_id)
            )

        if tournament:
            conditions.append(Match.tournament_name.ilike(f"%{tournament}%"))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_match(self, match_id: str) -> Optional[Match]:
        """Get a single match by ID"""

        query = select(Match).where(Match.id == match_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_match_with_players(self, match_id: str) -> Optional[Match]:
        """Get match with player details loaded"""

        query = (
            select(Match)
            .options(
                selectinload(Match.player1),
                selectinload(Match.player2)
            )
            .where(Match.id == match_id)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_match(self, match_data: MatchCreate) -> Match:
        """Create a new match"""

        match = Match(
            title=match_data.title,
            match_type=match_data.match_type,
            surface=match_data.surface,
            tournament_name=match_data.tournament_name,
            round_name=match_data.round_name,
            player1_id=match_data.player1_id,
            player2_id=match_data.player2_id,
            best_of_sets=match_data.best_of_sets,
            tiebreak_at=match_data.tiebreak_at,
            scheduled_at=match_data.scheduled_at,
            venue=match_data.venue,
            court_number=match_data.court_number,
            weather_conditions=match_data.weather_conditions,
            notes=match_data.notes,
            is_public=match_data.is_public
        )

        self.db.add(match)
        await self.db.commit()
        await self.db.refresh(match)

        logger.info("Match created", match_id=match.id, title=match.title)
        return match

    async def update_match(self, match_id: str, match_data: MatchUpdate) -> Optional[Match]:
        """Update an existing match"""

        match = await self.get_match(match_id)
        if not match:
            return None

        # Update fields that are provided
        update_data = match_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(match, field, value)

        match.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(match)

        logger.info("Match updated", match_id=match_id)
        return match

    async def delete_match(self, match_id: str) -> bool:
        """Delete a match"""

        match = await self.get_match(match_id)
        if not match:
            return False

        await self.db.delete(match)
        await self.db.commit()

        logger.info("Match deleted", match_id=match_id)
        return True

    async def start_match(self, match_id: str) -> Optional[Match]:
        """Start a scheduled match"""

        match = await self.get_match(match_id)
        if not match:
            return None

        if match.status != MatchStatus.SCHEDULED:
            raise ValueError(f"Match must be scheduled to start. Current status: {match.status}")

        match.status = MatchStatus.IN_PROGRESS
        match.started_at = datetime.utcnow()
        match.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(match)

        logger.info("Match started", match_id=match_id)
        return match

    async def finish_match(self, match_id: str) -> Optional[Match]:
        """Finish a match in progress"""

        match = await self.get_match(match_id)
        if not match:
            return None

        if match.status != MatchStatus.IN_PROGRESS:
            raise ValueError(f"Match must be in progress to finish. Current status: {match.status}")

        match.status = MatchStatus.COMPLETED
        match.finished_at = datetime.utcnow()
        match.updated_at = datetime.utcnow()

        # Calculate duration
        if match.started_at and match.finished_at:
            duration = match.finished_at - match.started_at
            match.duration_minutes = int(duration.total_seconds() / 60)

        await self.db.commit()
        await self.db.refresh(match)

        logger.info("Match finished", match_id=match_id, duration_minutes=match.duration_minutes)
        return match

    async def get_match_events(
        self,
        match_id: str,
        event_type: Optional[str] = None,
        limit: int = 1000
    ) -> MatchEventSummary:
        """Get events for a match"""

        # Get events
        events_query = (
            select(Event)
            .where(Event.match_id == match_id)
            .order_by(Event.timestamp)
            .limit(limit)
        )

        if event_type:
            events_query = events_query.where(Event.event_type == event_type)

        events_result = await self.db.execute(events_query)
        events = events_result.scalars().all()

        # Get points
        points_query = (
            select(Point)
            .where(Point.match_id == match_id)
            .order_by(Point.point_number)
        )
        points_result = await self.db.execute(points_query)
        points = points_result.scalars().all()

        # Get games
        games_query = (
            select(Game)
            .where(Game.match_id == match_id)
            .order_by(Game.game_number)
        )
        games_result = await self.db.execute(games_query)
        games = games_result.scalars().all()

        # Get sets
        sets_query = (
            select(Set)
            .where(Set.match_id == match_id)
            .order_by(Set.set_number)
        )
        sets_result = await self.db.execute(sets_query)
        sets = sets_result.scalars().all()

        return MatchEventSummary(
            match_id=match_id,
            events=[{
                "id": event.id,
                "type": event.event_type,
                "timestamp": event.timestamp,
                "player_id": event.player_id,
                "data": event.event_data
            } for event in events],
            points=[{
                "id": point.id,
                "number": point.point_number,
                "winner": point.winner_player_id,
                "outcome": point.outcome,
                "rally_length": point.rally_length
            } for point in points],
            games=[{
                "id": game.id,
                "number": game.game_number,
                "score": f"{game.player1_score}-{game.player2_score}",
                "winner": game.winner_player_id,
                "server": game.server_player_id
            } for game in games],
            sets=[{
                "id": set_.id,
                "number": set_.set_number,
                "score": f"{set_.player1_games}-{set_.player2_games}",
                "winner": set_.winner_player_id,
                "tiebreak": set_.is_tiebreak
            } for set_ in sets]
        )

    async def update_match_score(
        self,
        match_id: str,
        player1_sets: int,
        player2_sets: int,
        current_set: int
    ) -> Optional[Match]:
        """Update match score"""

        match = await self.get_match(match_id)
        if not match:
            return None

        match.player1_sets = player1_sets
        match.player2_sets = player2_sets
        match.current_set = current_set
        match.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(match)

        logger.info("Match score updated", match_id=match_id, score=f"{player1_sets}-{player2_sets}")
        return match

    async def add_match_event(
        self,
        match_id: str,
        event_type: str,
        event_data: dict,
        player_id: Optional[str] = None,
        point_id: Optional[str] = None
    ) -> Event:
        """Add an event to a match"""

        event = Event(
            match_id=match_id,
            point_id=point_id,
            event_type=event_type,
            player_id=player_id,
            event_data=event_data
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        logger.info("Match event added", match_id=match_id, event_type=event_type)
        return event