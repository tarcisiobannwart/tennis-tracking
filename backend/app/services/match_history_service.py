"""
Match History Service - TT-135
Service para listar e buscar historico de partidas com placares detalhados
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

import structlog
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.match import Match, MatchStatus
from app.models.player import Player
from app.models.set import Set
from app.models.game import Game

logger = structlog.get_logger(__name__)


class MatchHistoryService:
    """Service para operacoes de historico de partidas"""

    async def list_matches(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        match_type: Optional[str] = None,
        opponent_name: Optional[str] = None,
        surface: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Lista partidas do usuario com filtros e paginacao.

        Args:
            db: Sessao do banco de dados
            user_id: ID do usuario atual
            match_type: Tipo de partida (ranking/amistoso/torneio)
            opponent_name: Nome do oponente para filtrar
            surface: Superficie da quadra
            start_date: Data inicial
            end_date: Data final
            skip: Registros a pular
            limit: Limite de registros

        Returns:
            Dict com 'matches', 'total', 'page', 'limit', 'total_pages'
        """

        # Query base: partidas onde o usuario eh player1 ou player2
        query = (
            select(Match)
            .options(
                selectinload(Match.player1),
                selectinload(Match.player2),
                selectinload(Match.sets),
            )
            .where(
                and_(
                    or_(
                        Match.player1_id == str(user_id),
                        Match.player2_id == str(user_id),
                    ),
                    Match.status == MatchStatus.COMPLETED,  # Apenas partidas finalizadas
                )
            )
        )

        # Aplicar filtros
        filters = []

        if match_type:
            # Mapear tipos comuns
            if match_type.lower() == "ranking":
                filters.append(Match.tournament_name.ilike("%ranking%"))
            elif match_type.lower() == "amistoso":
                filters.append(
                    or_(
                        Match.tournament_name.ilike("%amistoso%"),
                        Match.tournament_name.ilike("%friendly%"),
                        Match.tournament_name.ilike("%treino%"),
                        Match.tournament_name.ilike("%training%"),
                    )
                )
            elif match_type.lower() == "torneio":
                filters.append(
                    and_(
                        Match.tournament_name.isnot(None),
                        ~Match.tournament_name.ilike("%amistoso%"),
                        ~Match.tournament_name.ilike("%friendly%"),
                        ~Match.tournament_name.ilike("%treino%"),
                        ~Match.tournament_name.ilike("%training%"),
                        ~Match.tournament_name.ilike("%ranking%"),
                    )
                )

        if opponent_name:
            # Buscar em ambos players (excluindo o usuario atual)
            filters.append(
                or_(
                    and_(
                        Match.player1_id != str(user_id),
                        select(Player.name)
                        .where(Player.id == Match.player1_id)
                        .correlate(Match)
                        .scalar_subquery()
                        .ilike(f"%{opponent_name}%"),
                    ),
                    and_(
                        Match.player2_id != str(user_id),
                        select(Player.name)
                        .where(Player.id == Match.player2_id)
                        .correlate(Match)
                        .scalar_subquery()
                        .ilike(f"%{opponent_name}%"),
                    ),
                )
            )

        if surface:
            filters.append(Match.surface == surface.lower())

        if start_date:
            filters.append(Match.finished_at >= start_date)

        if end_date:
            filters.append(Match.finished_at <= end_date)

        if filters:
            query = query.where(and_(*filters))

        # Ordenar por data (mais recentes primeiro)
        query = query.order_by(desc(Match.finished_at))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginacao
        query = query.offset(skip).limit(limit)

        # Executar query
        result = await db.execute(query)
        matches = result.scalars().all()

        # Formatar resposta
        formatted_matches = []
        for match in matches:
            # Determinar oponente
            is_player1 = str(match.player1_id) == str(user_id)
            opponent = match.player2 if is_player1 else match.player1
            user_sets = match.player1_sets if is_player1 else match.player2_sets
            opponent_sets = match.player2_sets if is_player1 else match.player1_sets

            # Determinar resultado
            result_type = "vitoria" if user_sets > opponent_sets else "derrota"

            # Formatar placar por sets
            sets_score = []
            for set_obj in sorted(match.sets, key=lambda s: s.set_number):
                user_games = set_obj.player1_games if is_player1 else set_obj.player2_games
                opponent_games = set_obj.player2_games if is_player1 else set_obj.player1_games

                set_dict = {
                    "set_number": set_obj.set_number,
                    "user_games": user_games,
                    "opponent_games": opponent_games,
                }

                # Tiebreak se houver
                if set_obj.is_tiebreak:
                    user_tiebreak = set_obj.player1_tiebreak if is_player1 else set_obj.player2_tiebreak
                    opponent_tiebreak = set_obj.player2_tiebreak if is_player1 else set_obj.player1_tiebreak
                    set_dict["user_tiebreak"] = user_tiebreak
                    set_dict["opponent_tiebreak"] = opponent_tiebreak

                sets_score.append(set_dict)

            # Classificar tipo de partida
            tournament_name = match.tournament_name or "Partida Amistosa"
            if "ranking" in tournament_name.lower():
                match_type_label = "ranking"
            elif any(
                keyword in tournament_name.lower()
                for keyword in ["amistoso", "friendly", "treino", "training"]
            ):
                match_type_label = "amistoso"
            else:
                match_type_label = "torneio"

            formatted_matches.append(
                {
                    "id": match.id,
                    "date": match.finished_at.isoformat() if match.finished_at else None,
                    "opponent": {
                        "id": opponent.id,
                        "name": opponent.name,
                        "avatar_url": getattr(opponent, "avatar_url", None),
                    },
                    "result": result_type,
                    "score": {
                        "sets": f"{user_sets}-{opponent_sets}",
                        "user_sets": user_sets,
                        "opponent_sets": opponent_sets,
                        "sets_detail": sets_score,
                    },
                    "match_type": match_type_label,
                    "tournament": tournament_name,
                    "venue": match.venue,
                    "surface": match.surface,
                    "duration_minutes": match.duration_minutes,
                }
            )

        # Calcular total de paginas
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        current_page = (skip // limit) + 1

        return {
            "matches": formatted_matches,
            "total": total,
            "page": current_page,
            "limit": limit,
            "total_pages": total_pages,
        }

    async def get_match_detail(
        self,
        db: AsyncSession,
        match_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna detalhes completos de uma partida.

        Args:
            db: Sessao do banco de dados
            match_id: ID da partida
            user_id: ID do usuario atual (para verificar acesso)

        Returns:
            Dict com detalhes completos ou None se nao encontrado
        """

        # Buscar partida com relacionamentos
        query = (
            select(Match)
            .options(
                selectinload(Match.player1),
                selectinload(Match.player2),
                selectinload(Match.sets).selectinload(Set.games),
            )
            .where(
                and_(
                    Match.id == str(match_id),
                    or_(
                        Match.player1_id == str(user_id),
                        Match.player2_id == str(user_id),
                    ),
                )
            )
        )

        result = await db.execute(query)
        match = result.scalar_one_or_none()

        if not match:
            return None

        # Determinar se usuario eh player1
        is_player1 = str(match.player1_id) == str(user_id)
        opponent = match.player2 if is_player1 else match.player1
        user_sets = match.player1_sets if is_player1 else match.player2_sets
        opponent_sets = match.player2_sets if is_player1 else match.player1_sets

        # Resultado
        result_type = "vitoria" if user_sets > opponent_sets else "derrota"

        # Detalhes dos sets com games
        sets_detail = []
        for set_obj in sorted(match.sets, key=lambda s: s.set_number):
            user_games = set_obj.player1_games if is_player1 else set_obj.player2_games
            opponent_games = set_obj.player2_games if is_player1 else set_obj.player1_games

            set_dict = {
                "set_number": set_obj.set_number,
                "user_games": user_games,
                "opponent_games": opponent_games,
                "winner": "user" if (
                    (is_player1 and set_obj.winner_player_id == match.player1_id) or
                    (not is_player1 and set_obj.winner_player_id == match.player2_id)
                ) else "opponent",
            }

            # Tiebreak
            if set_obj.is_tiebreak:
                user_tiebreak = set_obj.player1_tiebreak if is_player1 else set_obj.player2_tiebreak
                opponent_tiebreak = set_obj.player2_tiebreak if is_player1 else set_obj.player1_tiebreak
                set_dict["is_tiebreak"] = True
                set_dict["user_tiebreak"] = user_tiebreak
                set_dict["opponent_tiebreak"] = opponent_tiebreak
            else:
                set_dict["is_tiebreak"] = False

            # Games detalhados (se disponiveis)
            games_detail = []
            if set_obj.games:
                for game in sorted(set_obj.games, key=lambda g: g.game_number):
                    games_detail.append(
                        {
                            "game_number": game.game_number,
                            "winner": "user" if (
                                (is_player1 and game.winner_player_id == match.player1_id) or
                                (not is_player1 and game.winner_player_id == match.player2_id)
                            ) else "opponent",
                            "server": "user" if (
                                (is_player1 and game.server_player_id == match.player1_id) or
                                (not is_player1 and game.server_player_id == match.player2_id)
                            ) else "opponent",
                        }
                    )
            set_dict["games"] = games_detail

            sets_detail.append(set_dict)

        # Classificar tipo
        tournament_name = match.tournament_name or "Partida Amistosa"
        if "ranking" in tournament_name.lower():
            match_type_label = "ranking"
        elif any(
            keyword in tournament_name.lower()
            for keyword in ["amistoso", "friendly", "treino", "training"]
        ):
            match_type_label = "amistoso"
        else:
            match_type_label = "torneio"

        return {
            "id": match.id,
            "title": match.title,
            "date": match.finished_at.isoformat() if match.finished_at else None,
            "started_at": match.started_at.isoformat() if match.started_at else None,
            "user": {
                "id": match.player1.id if is_player1 else match.player2.id,
                "name": match.player1.name if is_player1 else match.player2.name,
                "avatar_url": getattr(
                    match.player1 if is_player1 else match.player2, "avatar_url", None
                ),
            },
            "opponent": {
                "id": opponent.id,
                "name": opponent.name,
                "avatar_url": getattr(opponent, "avatar_url", None),
            },
            "result": result_type,
            "score": {
                "sets": f"{user_sets}-{opponent_sets}",
                "user_sets": user_sets,
                "opponent_sets": opponent_sets,
                "sets_detail": sets_detail,
            },
            "match_type": match_type_label,
            "tournament": tournament_name,
            "round_name": match.round_name,
            "venue": match.venue,
            "court_number": match.court_number,
            "surface": match.surface,
            "duration_minutes": match.duration_minutes,
            "best_of_sets": match.best_of_sets,
            "weather_conditions": match.weather_conditions,
            "notes": match.notes,
        }
