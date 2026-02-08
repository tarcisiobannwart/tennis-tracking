"""
H2H (Head to Head) Service - TT-134
Service para calcular comparativos H2H entre jogadores
"""

import uuid
from typing import Optional, Dict, Any, List
from collections import defaultdict

import structlog
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.match import Match, MatchStatus
from app.models.player import Player
from app.models.set import Set

logger = structlog.get_logger(__name__)


class H2HService:
    """Service para operacoes de Head to Head"""

    def _format_player_profile(self, player: Player) -> Dict[str, Any]:
        """Formata perfil do jogador"""
        hand_labels = {
            "right": "Destro",
            "left": "Canhoto",
            "ambidextrous": "Ambidestro",
        }
        return {
            "id": player.id,
            "name": player.name,
            "avatar_url": getattr(player, "profile_image_url", None) or getattr(player, "avatar_url", None),
            "age": player.age,
            "height": player.height,
            "dominant_hand": player.dominant_hand,
            "country": player.country,
            "ranking": player.ranking,
            "skill_level": player.skill_level,
        }

    def _build_comparison(self, player: Player, opponent: Player) -> List[Dict[str, str]]:
        """Constroi tabela comparativa entre dois jogadores"""
        hand_labels = {
            "right": "Destro",
            "left": "Canhoto",
            "ambidextrous": "Ambidestro",
        }

        comparison = []

        # Idade
        comparison.append({
            "attribute": "age",
            "label": "Idade",
            "player_value": str(player.age) if player.age else "-",
            "opponent_value": str(opponent.age) if opponent.age else "-",
        })

        # Altura
        comparison.append({
            "attribute": "height",
            "label": "Altura",
            "player_value": f"{player.height:.0f} cm" if player.height else "-",
            "opponent_value": f"{opponent.height:.0f} cm" if opponent.height else "-",
        })

        # Lateralidade
        comparison.append({
            "attribute": "dominant_hand",
            "label": "Lateralidade",
            "player_value": hand_labels.get(player.dominant_hand or "", "-"),
            "opponent_value": hand_labels.get(opponent.dominant_hand or "", "-"),
        })

        # Pais
        comparison.append({
            "attribute": "country",
            "label": "Pais",
            "player_value": player.country or "-",
            "opponent_value": opponent.country or "-",
        })

        # Ranking
        comparison.append({
            "attribute": "ranking",
            "label": "Ranking",
            "player_value": f"#{player.ranking}" if player.ranking else "-",
            "opponent_value": f"#{opponent.ranking}" if opponent.ranking else "-",
        })

        # Nivel
        skill_labels = {
            "beginner": "Iniciante",
            "intermediate": "Intermediario",
            "advanced": "Avancado",
            "professional": "Profissional",
        }
        comparison.append({
            "attribute": "skill_level",
            "label": "Nivel",
            "player_value": skill_labels.get(player.skill_level or "", "-"),
            "opponent_value": skill_labels.get(opponent.skill_level or "", "-"),
        })

        return comparison

    async def get_h2h(
        self,
        db: AsyncSession,
        player_id: uuid.UUID,
        opponent_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Retorna dados completos do H2H entre dois jogadores.

        Args:
            db: Sessao do banco de dados
            player_id: ID do jogador principal
            opponent_id: ID do adversario

        Returns:
            Dict com todos os dados do H2H
        """
        # Buscar perfis dos jogadores
        player_query = select(Player).where(Player.id == str(player_id))
        opponent_query = select(Player).where(Player.id == str(opponent_id))

        player_result = await db.execute(player_query)
        opponent_result = await db.execute(opponent_query)

        player = player_result.scalar_one_or_none()
        opponent = opponent_result.scalar_one_or_none()

        if not player or not opponent:
            return None

        # Buscar todas as partidas entre os dois jogadores
        matches_query = (
            select(Match)
            .options(
                selectinload(Match.sets),
            )
            .where(
                and_(
                    Match.status == MatchStatus.COMPLETED,
                    or_(
                        and_(
                            Match.player1_id == str(player_id),
                            Match.player2_id == str(opponent_id),
                        ),
                        and_(
                            Match.player1_id == str(opponent_id),
                            Match.player2_id == str(player_id),
                        ),
                    ),
                )
            )
            .order_by(desc(Match.finished_at))
        )

        result = await db.execute(matches_query)
        matches = result.scalars().all()

        # Calcular H2H
        h2h_score = {"player_wins": 0, "opponent_wins": 0}
        match_history = []
        sets_games_over_time = []
        total_sets_player = 0
        total_sets_opponent = 0
        total_games_player = 0
        total_games_opponent = 0

        for match in matches:
            is_player1 = str(match.player1_id) == str(player_id)
            p_sets = match.player1_sets if is_player1 else match.player2_sets
            o_sets = match.player2_sets if is_player1 else match.player1_sets
            is_win = p_sets > o_sets

            if is_win:
                h2h_score["player_wins"] += 1
            else:
                h2h_score["opponent_wins"] += 1

            total_sets_player += p_sets
            total_sets_opponent += o_sets

            # Calcular games totais
            p_games = 0
            o_games = 0
            sets_detail = []

            for set_obj in sorted(match.sets, key=lambda s: s.set_number):
                user_games = set_obj.player1_games if is_player1 else set_obj.player2_games
                opp_games = set_obj.player2_games if is_player1 else set_obj.player1_games
                p_games += user_games
                o_games += opp_games

                set_dict = {
                    "set_number": set_obj.set_number,
                    "player_games": user_games,
                    "opponent_games": opp_games,
                }
                if set_obj.is_tiebreak:
                    set_dict["player_tiebreak"] = set_obj.player1_tiebreak if is_player1 else set_obj.player2_tiebreak
                    set_dict["opponent_tiebreak"] = set_obj.player2_tiebreak if is_player1 else set_obj.player1_tiebreak
                sets_detail.append(set_dict)

            total_games_player += p_games
            total_games_opponent += o_games

            # Match history item
            match_date = match.finished_at.isoformat() if match.finished_at else None
            match_history.append({
                "match_id": match.id,
                "date": match_date,
                "result": "win" if is_win else "loss",
                "player_sets": p_sets,
                "opponent_sets": o_sets,
                "sets_detail": sets_detail,
                "tournament": match.tournament_name,
                "surface": match.surface,
                "venue": match.venue,
                "duration_minutes": match.duration_minutes,
            })

            # Sets/Games over time
            if match.finished_at:
                month_label = match.finished_at.strftime("%b %Y")
                sets_games_over_time.append({
                    "match_date": match_date,
                    "match_label": month_label,
                    "player_sets": p_sets,
                    "opponent_sets": o_sets,
                    "player_games": p_games,
                    "opponent_games": o_games,
                })

        # Inverter para ordem cronologica nos graficos
        sets_games_over_time.reverse()

        # Comparacao
        comparison = self._build_comparison(player, opponent)

        # Adicionar estatisticas V/D na comparacao
        comparison.append({
            "attribute": "wins",
            "label": "Vitorias Gerais",
            "player_value": str(h2h_score["player_wins"]),
            "opponent_value": str(h2h_score["opponent_wins"]),
        })

        return {
            "player": self._format_player_profile(player),
            "opponent": self._format_player_profile(opponent),
            "h2h_score": h2h_score,
            "comparison": comparison,
            "sets_games_over_time": sets_games_over_time,
            "match_history": match_history,
            "total_matches": len(matches),
            "total_sets_player": total_sets_player,
            "total_sets_opponent": total_sets_opponent,
            "total_games_player": total_games_player,
            "total_games_opponent": total_games_opponent,
        }

    async def get_opponents_list(
        self,
        db: AsyncSession,
        player_id: uuid.UUID,
    ) -> List[Dict[str, Any]]:
        """
        Lista todos os adversarios com H2H resumido.

        Args:
            db: Sessao do banco de dados
            player_id: ID do jogador principal

        Returns:
            Lista de adversarios com resumo H2H
        """
        # Buscar todas as partidas do jogador
        matches_query = (
            select(Match)
            .options(
                selectinload(Match.player1),
                selectinload(Match.player2),
            )
            .where(
                and_(
                    Match.status == MatchStatus.COMPLETED,
                    or_(
                        Match.player1_id == str(player_id),
                        Match.player2_id == str(player_id),
                    ),
                )
            )
            .order_by(desc(Match.finished_at))
        )

        result = await db.execute(matches_query)
        matches = result.scalars().all()

        # Agrupar por adversario
        opponents: Dict[str, Dict[str, Any]] = {}

        for match in matches:
            is_player1 = str(match.player1_id) == str(player_id)
            opponent = match.player2 if is_player1 else match.player1
            p_sets = match.player1_sets if is_player1 else match.player2_sets
            o_sets = match.player2_sets if is_player1 else match.player1_sets
            is_win = p_sets > o_sets

            opp_id = opponent.id

            if opp_id not in opponents:
                opponents[opp_id] = {
                    "id": opp_id,
                    "name": opponent.name,
                    "avatar_url": getattr(opponent, "profile_image_url", None) or getattr(opponent, "avatar_url", None),
                    "total_matches": 0,
                    "player_wins": 0,
                    "opponent_wins": 0,
                    "last_match_date": None,
                }

            opponents[opp_id]["total_matches"] += 1
            if is_win:
                opponents[opp_id]["player_wins"] += 1
            else:
                opponents[opp_id]["opponent_wins"] += 1

            # Atualizar last_match_date (partidas ja vem ordenadas desc)
            if not opponents[opp_id]["last_match_date"] and match.finished_at:
                opponents[opp_id]["last_match_date"] = match.finished_at.isoformat()

        # Ordenar por total de partidas (desc)
        sorted_opponents = sorted(
            opponents.values(),
            key=lambda x: x["total_matches"],
            reverse=True,
        )

        return sorted_opponents

    async def get_h2h_matches(
        self,
        db: AsyncSession,
        player_id: uuid.UUID,
        opponent_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Retorna historico de confrontos diretos com paginacao.

        Args:
            db: Sessao do banco de dados
            player_id: ID do jogador principal
            opponent_id: ID do adversario
            skip: Registros a pular
            limit: Limite de registros

        Returns:
            Dict com matches e paginacao
        """
        h2h_data = await self.get_h2h(db, player_id, opponent_id)

        if not h2h_data:
            return {"matches": [], "total": 0}

        all_matches = h2h_data["match_history"]
        total = len(all_matches)
        paginated = all_matches[skip:skip + limit]

        return {
            "matches": paginated,
            "total": total,
            "h2h_score": h2h_data["h2h_score"],
        }
