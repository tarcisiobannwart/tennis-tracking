"""
Player service for business logic operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from typing import List, Optional
from datetime import datetime
import structlog

from app.models.player import Player
from app.models.match import Match
from app.schemas.player import PlayerCreate, PlayerUpdate

logger = structlog.get_logger(__name__)


class PlayerService:
    """Service for player-related operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_players(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        country: Optional[str] = None,
        skill_level: Optional[str] = None,
        is_active: bool = True
    ) -> List[Player]:
        """Get players with optional filtering"""

        query = select(Player).where(Player.is_active == is_active)

        # Apply filters
        if search:
            query = query.where(Player.name.ilike(f"%{search}%"))

        if country:
            query = query.where(Player.country == country)

        if skill_level:
            query = query.where(Player.skill_level == skill_level)

        query = query.order_by(desc(Player.created_at)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a single player by ID"""

        query = select(Player).where(Player.id == player_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_player(self, player_data: PlayerCreate) -> Player:
        """Create a new player"""

        player = Player(
            name=player_data.name,
            email=player_data.email,
            age=player_data.age,
            country=player_data.country,
            height=player_data.height,
            weight=player_data.weight,
            dominant_hand=player_data.dominant_hand,
            ranking=player_data.ranking,
            skill_level=player_data.skill_level,
            bio=player_data.bio,
            profile_image_url=player_data.profile_image_url
        )

        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)

        logger.info("Player created", player_id=player.id, name=player.name)
        return player

    async def update_player(self, player_id: str, player_data: PlayerUpdate) -> Optional[Player]:
        """Update an existing player"""

        player = await self.get_player(player_id)
        if not player:
            return None

        # Update fields that are provided
        update_data = player_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(player, field, value)

        player.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(player)

        logger.info("Player updated", player_id=player_id)
        return player

    async def delete_player(self, player_id: str) -> bool:
        """Soft delete a player (mark as inactive)"""

        player = await self.get_player(player_id)
        if not player:
            return False

        player.is_active = False
        player.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info("Player deleted (soft)", player_id=player_id)
        return True

    async def get_player_matches(
        self,
        player_id: str,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        surface: Optional[str] = None
    ) -> List[Match]:
        """Get matches for a specific player"""

        query = select(Match).where(
            or_(Match.player1_id == player_id, Match.player2_id == player_id)
        )

        # Apply filters
        if status:
            query = query.where(Match.status == status)

        if surface:
            query = query.where(Match.surface == surface)

        query = query.order_by(desc(Match.created_at)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_recent_form(self, player_id: str, matches: int = 10) -> dict:
        """Get recent form for a player"""

        # Get recent matches
        recent_matches = await self.get_player_matches(
            player_id,
            limit=matches,
            status="completed"
        )

        results = []
        wins = 0
        losses = 0

        for match in recent_matches:
            # Determine if player won
            if match.status == "completed":
                # Simple logic - can be enhanced with actual set scores
                if match.player1_id == player_id:
                    won = match.player1_sets > match.player2_sets
                else:
                    won = match.player2_sets > match.player1_sets

                result = "W" if won else "L"
                results.append(result)

                if won:
                    wins += 1
                else:
                    losses += 1

        win_percentage = (wins / len(results)) * 100 if results else 0

        return {
            "results": results,
            "wins": wins,
            "losses": losses,
            "win_percentage": win_percentage
        }

    async def search_by_ranking(
        self,
        min_ranking: Optional[int] = None,
        max_ranking: Optional[int] = None,
        limit: int = 50
    ) -> List[Player]:
        """Search players by ranking range"""

        query = select(Player).where(Player.is_active == True)

        # Apply ranking filters
        if min_ranking is not None:
            query = query.where(Player.ranking >= min_ranking)

        if max_ranking is not None:
            query = query.where(Player.ranking <= max_ranking)

        # Order by ranking
        query = query.order_by(Player.ranking.asc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()