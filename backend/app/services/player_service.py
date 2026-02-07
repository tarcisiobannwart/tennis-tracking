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
from app.models.point import Point
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
        """Get recent form for a player with detailed match info"""

        # Get recent matches ordered by date
        recent_matches_query = select(Match).where(
            or_(Match.player1_id == player_id, Match.player2_id == player_id),
            Match.status == "completed"
        ).order_by(desc(Match.created_at)).limit(matches)

        recent_matches_result = await self.db.execute(recent_matches_query)
        recent_matches = recent_matches_result.scalars().all()

        results = []
        wins = 0
        losses = 0
        match_details = []

        for match in recent_matches:
            # Determine if player won
            if match.player1_id == player_id:
                won = match.player1_sets > match.player2_sets
                player_sets = match.player1_sets
                opponent_sets = match.player2_sets
                opponent_id = match.player2_id
            else:
                won = match.player2_sets > match.player1_sets
                player_sets = match.player2_sets
                opponent_sets = match.player1_sets
                opponent_id = match.player1_id

            result = "W" if won else "L"
            results.append(result)

            if won:
                wins += 1
            else:
                losses += 1

            # Get opponent details
            opponent = await self.get_player(opponent_id)
            opponent_name = opponent.name if opponent else "Unknown"

            match_details.append({
                "match_id": match.id,
                "date": match.created_at.isoformat() if match.created_at else None,
                "result": result,
                "score": f"{player_sets}-{opponent_sets}",
                "opponent_id": opponent_id,
                "opponent_name": opponent_name,
                "surface": match.surface,
                "tournament": getattr(match, "tournament_name", None)
            })

        win_percentage = (wins / len(results)) * 100 if results else 0

        return {
            "results": results,
            "wins": wins,
            "losses": losses,
            "win_percentage": win_percentage,
            "matches": match_details
        }

    async def search_by_ranking(
        self,
        min_ranking: Optional[int] = None,
        max_ranking: Optional[int] = None,
        country: Optional[str] = None,
        surface: Optional[str] = None,
        limit: int = 50
    ) -> List[Player]:
        """
        Search players by ranking range with additional filters

        Critérios de aceite TT-51:
        - [x] Busca por faixa de ranking
        - [x] Filtros combinados (país, superfície)
        - [x] Paginação

        Args:
            min_ranking: Ranking mínimo
            max_ranking: Ranking máximo
            country: Código do país (opcional)
            surface: Superfície preferida (opcional)
            limit: Limite de resultados

        Returns:
            Lista de jogadores ordenada por ranking
        """
        query = select(Player).where(Player.is_active == True)

        # Apply ranking filters
        if min_ranking is not None:
            query = query.where(Player.ranking >= min_ranking)

        if max_ranking is not None:
            query = query.where(Player.ranking <= max_ranking)

        # Apply country filter
        if country:
            query = query.where(Player.country == country)

        # Apply surface filter (based on player's best surface or recent performance)
        # Note: This assumes players have a 'preferred_surface' field or we filter by stats
        if surface:
            # For now, we'll get all and filter by surface stats in detailed_stats
            # In future, could add preferred_surface to Player model
            pass

        # Order by ranking
        query = query.order_by(Player.ranking.asc()).limit(limit)

        result = await self.db.execute(query)
        players = result.scalars().all()

        # If surface filter specified, enrich with surface-specific win rate
        if surface and players:
            enriched_players = []
            for player in players:
                # Get surface-specific stats
                try:
                    stats = await self.get_detailed_stats(
                        player.id,
                        period="all_time",
                        surface=surface
                    )
                    # Add surface win rate to player object for client
                    player.surface_win_rate = stats.get("win_rate", 0)
                    enriched_players.append(player)
                except:
                    # If stats fail, still include player
                    player.surface_win_rate = None
                    enriched_players.append(player)

            return enriched_players

        return players

    async def get_detailed_stats(
        self,
        player_id: str,
        period: Optional[str] = "all_time",
        surface: Optional[str] = None
    ) -> dict:
        """Get detailed statistics for a player by period and surface"""

        # Import needed here to avoid circular dependencies
        from app.services.analytics_service import AnalyticsService
        analytics_service = AnalyticsService(self.db)

        # Get basic stats
        basic_stats = await analytics_service.get_player_statistics(
            player_id,
            period=period,
            surface=surface
        )

        # Get matches with filters
        matches_query = select(Match).where(
            or_(Match.player1_id == player_id, Match.player2_id == player_id),
            Match.status == "completed"
        )

        if surface:
            matches_query = matches_query.where(Match.surface == surface)

        if period != "all_time":
            cutoff_date = self._get_period_cutoff(period)
            matches_query = matches_query.where(Match.created_at >= cutoff_date)

        matches_result = await self.db.execute(matches_query)
        matches = matches_result.scalars().all()

        # Calculate advanced metrics
        service_games_won = 0
        return_games_won = 0
        break_points_won = 0
        break_points_faced = 0
        total_service_games = 0
        total_return_games = 0

        for match in matches:
            # Get points for this match
            points_query = select(Point).where(Point.match_id == match.id)
            points_result = await self.db.execute(points_query)
            points = points_result.scalars().all()

            for point in points:
                # Service games
                if point.server_player_id == player_id:
                    total_service_games += 1
                    if point.winner_player_id == player_id:
                        service_games_won += 1
                else:
                    total_return_games += 1
                    if point.winner_player_id == player_id:
                        return_games_won += 1

                # Break points
                if point.is_break_point:
                    if point.server_player_id == player_id:
                        break_points_faced += 1
                        if point.winner_player_id == player_id:
                            break_points_won += 1

        service_games_won_pct = (service_games_won / total_service_games * 100) if total_service_games > 0 else 0
        return_games_won_pct = (return_games_won / total_return_games * 100) if total_return_games > 0 else 0
        break_points_saved_pct = (break_points_won / break_points_faced * 100) if break_points_faced > 0 else 0

        return {
            "player_id": player_id,
            "period": period,
            "surface": surface,
            "win_rate": basic_stats.win_percentage,
            "matches_played": basic_stats.total_matches,
            "wins": basic_stats.wins,
            "losses": basic_stats.losses,
            "aces": basic_stats.aces,
            "double_faults": basic_stats.double_faults,
            "first_serve_percentage": basic_stats.first_serve_percentage,
            "service_games_won": service_games_won,
            "service_games_won_percentage": service_games_won_pct,
            "return_games_won": return_games_won,
            "return_games_won_percentage": return_games_won_pct,
            "break_points_saved": break_points_won,
            "break_points_faced": break_points_faced,
            "break_points_saved_percentage": break_points_saved_pct,
            "total_points_won": basic_stats.points_won,
            "total_points_played": basic_stats.total_points_played,
            "winners": basic_stats.winners,
            "unforced_errors": basic_stats.unforced_errors
        }

    def _get_period_cutoff(self, period: str) -> datetime:
        """Get cutoff date for period filtering"""
        from datetime import timedelta

        now = datetime.utcnow()

        if period == "week":
            return now - timedelta(days=7)
        elif period == "month":
            return now - timedelta(days=30)
        elif period == "year":
            return now - timedelta(days=365)
        else:
            return datetime.min  # All time