"""
Search Service - busca global unificada.

Implementado para TT-138: Busca global de jogadores, locais, rankings e torneios.
"""

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.sql.user import User
from app.models.sql.venue import Venue
from app.models.sql.tournament import Tournament

logger = structlog.get_logger(__name__)


class SearchService:
    """Servico para busca global unificada."""

    @staticmethod
    async def search_all(
        db: AsyncSession,
        query: str,
        limit: int = 5,
    ) -> dict:
        """
        Busca global em todas as entidades.

        Args:
            db: Sessao do banco de dados
            query: Termo de busca
            limit: Limite de resultados por categoria

        Returns:
            Dicionario com resultados agrupados por categoria
        """
        try:
            results = {
                "players": [],
                "venues": [],
                "rankings": [],
                "tournaments": [],
            }

            # Buscar jogadores (users)
            players_query = (
                select(User)
                .where(
                    or_(
                        func.lower(User.full_name).contains(query.lower()),
                        func.lower(User.username).contains(query.lower()),
                    )
                )
                .limit(limit)
            )
            players_result = await db.execute(players_query)
            players = players_result.scalars().all()

            results["players"] = [
                {
                    "id": str(player.id),
                    "name": player.full_name,
                    "avatar_url": player.avatar_url,
                    "username": player.username,
                }
                for player in players
            ]

            # Buscar locais/clubes/academias
            venues_query = (
                select(Venue)
                .where(
                    or_(
                        func.lower(Venue.name).contains(query.lower()),
                        func.lower(Venue.city).contains(query.lower()) if hasattr(Venue, 'city') else False,
                    )
                )
                .limit(limit)
            )
            venues_result = await db.execute(venues_query)
            venues = venues_result.scalars().all()

            results["venues"] = [
                {
                    "id": str(venue.id),
                    "name": venue.name,
                    "city": venue.city if hasattr(venue, 'city') else None,
                    "type": venue.type if hasattr(venue, 'type') else "venue",
                }
                for venue in venues
            ]

            # Buscar rankings (usando tabela de torneios como proxy por enquanto)
            # Em uma implementacao real, voce teria uma tabela separada de rankings
            rankings_query = (
                select(Tournament)
                .where(
                    func.lower(Tournament.name).contains(query.lower())
                )
                .limit(limit)
            )
            rankings_result = await db.execute(rankings_query)
            rankings = rankings_result.scalars().all()

            results["rankings"] = [
                {
                    "id": str(ranking.id),
                    "name": ranking.name,
                    "category": ranking.category if hasattr(ranking, 'category') else None,
                }
                for ranking in rankings[:2]  # Limitar para mostrar poucos rankings
            ]

            # Buscar torneios
            tournaments_query = (
                select(Tournament)
                .where(
                    func.lower(Tournament.name).contains(query.lower())
                )
                .limit(limit)
            )
            tournaments_result = await db.execute(tournaments_query)
            tournaments = tournaments_result.scalars().all()

            results["tournaments"] = [
                {
                    "id": str(tournament.id),
                    "name": tournament.name,
                    "date": tournament.start_date.isoformat() if hasattr(tournament, 'start_date') and tournament.start_date else None,
                    "status": tournament.status if hasattr(tournament, 'status') else "upcoming",
                }
                for tournament in tournaments
            ]

            logger.info(
                "Busca global realizada",
                query=query,
                players_count=len(results["players"]),
                venues_count=len(results["venues"]),
                rankings_count=len(results["rankings"]),
                tournaments_count=len(results["tournaments"]),
            )

            return results

        except Exception as e:
            logger.error("Erro ao realizar busca global", error=str(e), query=query)
            raise
