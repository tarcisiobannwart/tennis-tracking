"""
Statistics Service - TT-133
Service para calcular estatisticas avancadas a partir do historico de partidas
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import defaultdict

import structlog
from sqlalchemy import select, and_, or_, func, desc, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.match import Match, MatchStatus
from app.models.player import Player

logger = structlog.get_logger(__name__)


class StatisticsService:
    """Service para operacoes de estatisticas avancadas"""

    def _classify_match_type(self, tournament_name: Optional[str]) -> str:
        """Classifica o tipo de partida baseado no nome do torneio"""
        if not tournament_name:
            return "amistoso"
        name_lower = tournament_name.lower()
        if "ranking" in name_lower:
            return "ranking"
        if any(kw in name_lower for kw in ["amistoso", "friendly", "treino", "training"]):
            return "amistoso"
        if any(kw in name_lower for kw in ["torneio", "tournament", "copa", "open"]):
            return "torneio"
        if "dupla" in name_lower or "double" in name_lower:
            return "duplas"
        return "torneio"

    def _get_age_group(self, age: Optional[int]) -> str:
        """Retorna a faixa etaria"""
        if not age:
            return "Desconhecido"
        if age < 18:
            return "Sub-18"
        if age <= 25:
            return "18-25"
        if age <= 35:
            return "26-35"
        if age <= 45:
            return "36-45"
        if age <= 55:
            return "46-55"
        return "56+"

    def _get_surface_label(self, surface: Optional[str]) -> str:
        """Retorna o label legivel da superficie"""
        labels = {
            "clay": "Saibro",
            "hard": "Hard Court",
            "grass": "Grama",
            "carpet": "Carpete",
        }
        return labels.get(surface or "", "Desconhecido")

    async def get_dashboard(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        months: int = 12,
    ) -> Dict[str, Any]:
        """
        Retorna todos os dados do dashboard de estatisticas.

        Args:
            db: Sessao do banco de dados
            user_id: ID do usuario atual
            months: Numero de meses para considerar nos graficos mensais

        Returns:
            Dict com todos os dados do dashboard
        """
        # Buscar todas as partidas finalizadas do usuario
        query = (
            select(Match)
            .options(
                selectinload(Match.player1),
                selectinload(Match.player2),
            )
            .where(
                and_(
                    or_(
                        Match.player1_id == str(user_id),
                        Match.player2_id == str(user_id),
                    ),
                    Match.status == MatchStatus.COMPLETED,
                )
            )
            .order_by(desc(Match.finished_at))
        )

        result = await db.execute(query)
        matches = result.scalars().all()

        # Processar dados
        overall = {"total_matches": 0, "wins": 0, "losses": 0}
        by_type: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        by_result_type: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        monthly: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        by_surface: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        by_handedness: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        by_backhand: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        by_age_group: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        streak: List[Dict[str, Any]] = []

        for match in matches:
            is_player1 = str(match.player1_id) == str(user_id)
            user_sets = match.player1_sets if is_player1 else match.player2_sets
            opponent_sets = match.player2_sets if is_player1 else match.player1_sets
            opponent = match.player2 if is_player1 else match.player1
            is_win = user_sets > opponent_sets

            # Overall
            overall["total_matches"] += 1
            if is_win:
                overall["wins"] += 1
            else:
                overall["losses"] += 1

            # By type
            match_type = self._classify_match_type(match.tournament_name)
            by_type[match_type]["total"] += 1
            if is_win:
                by_type[match_type]["wins"] += 1
            else:
                by_type[match_type]["losses"] += 1

            # By result type (jogado, W.O., desistencia)
            # Deduzimos pelo placar - se ambos tem 0 sets, pode ser W.O.
            if user_sets == 0 and opponent_sets == 0:
                result_type = "wo"
            elif match.notes and any(kw in (match.notes or "").lower() for kw in ["desistencia", "withdrawal", "retired"]):
                result_type = "withdrawal"
            else:
                result_type = "played"

            by_result_type[result_type]["total"] += 1
            if is_win:
                by_result_type[result_type]["wins"] += 1
            else:
                by_result_type[result_type]["losses"] += 1

            # Monthly
            if match.finished_at:
                month_key = match.finished_at.strftime("%Y-%m")
                monthly[month_key]["total"] += 1
                if is_win:
                    monthly[month_key]["wins"] += 1
                else:
                    monthly[month_key]["losses"] += 1

            # By surface
            surface = match.surface or "unknown"
            by_surface[surface]["total"] += 1
            if is_win:
                by_surface[surface]["wins"] += 1
            else:
                by_surface[surface]["losses"] += 1

            # Opponent profile
            if opponent:
                # Handedness
                hand = opponent.dominant_hand or "unknown"
                hand_label = {
                    "right": "Destro",
                    "left": "Canhoto",
                    "ambidextrous": "Ambidestro",
                    "unknown": "Desconhecido",
                }.get(hand, "Desconhecido")
                by_handedness[hand_label]["total"] += 1
                if is_win:
                    by_handedness[hand_label]["wins"] += 1
                else:
                    by_handedness[hand_label]["losses"] += 1

                # Age group
                age_group = self._get_age_group(opponent.age)
                by_age_group[age_group]["total"] += 1
                if is_win:
                    by_age_group[age_group]["wins"] += 1
                else:
                    by_age_group[age_group]["losses"] += 1

            # Streak (ultimos 30 jogos)
            if len(streak) < 30:
                streak.append({
                    "match_id": match.id,
                    "date": match.finished_at.isoformat() if match.finished_at else "",
                    "result": "V" if is_win else "D",
                    "opponent_name": opponent.name if opponent else "Desconhecido",
                })

        # Calcular win rates
        win_rate = (overall["wins"] / overall["total_matches"] * 100) if overall["total_matches"] > 0 else 0.0

        # Formatar monthly (ultimos N meses)
        now = datetime.utcnow()
        monthly_list = []
        for i in range(months - 1, -1, -1):
            dt = now - timedelta(days=i * 30)
            month_key = dt.strftime("%Y-%m")
            month_label = dt.strftime("%b %Y")
            data = monthly.get(month_key, {"total": 0, "wins": 0, "losses": 0})
            monthly_list.append({
                "month": month_key,
                "label": month_label,
                "total": data["total"],
                "wins": data["wins"],
                "losses": data["losses"],
            })

        # Formatar by_type
        type_labels = {
            "ranking": "Rankings",
            "torneio": "Torneios",
            "amistoso": "Amistosos",
            "duplas": "Duplas",
        }
        by_type_list = []
        for key, data in by_type.items():
            total = data["total"]
            wr = (data["wins"] / total * 100) if total > 0 else 0.0
            by_type_list.append({
                "label": type_labels.get(key, key.capitalize()),
                "total": total,
                "wins": data["wins"],
                "losses": data["losses"],
                "win_rate": round(wr, 1),
            })

        # Formatar by_result_type
        result_type_labels = {
            "played": "Jogado",
            "wo": "W.O.",
            "withdrawal": "Desistencia",
        }
        by_result_type_list = []
        for key, data in by_result_type.items():
            by_result_type_list.append({
                "result_type": key,
                "label": result_type_labels.get(key, key),
                "total": data["total"],
                "wins": data["wins"],
                "losses": data["losses"],
            })

        # Formatar by_surface
        by_surface_list = []
        for key, data in by_surface.items():
            if key == "unknown":
                continue
            total = data["total"]
            wr = (data["wins"] / total * 100) if total > 0 else 0.0
            by_surface_list.append({
                "surface": key,
                "label": self._get_surface_label(key),
                "total": total,
                "wins": data["wins"],
                "losses": data["losses"],
                "win_rate": round(wr, 1),
            })

        # Formatar opponent profile
        handedness_list = []
        for key, data in by_handedness.items():
            if key == "Desconhecido":
                continue
            total = data["total"]
            wr = (data["wins"] / total * 100) if total > 0 else 0.0
            handedness_list.append({
                "label": key,
                "total": total,
                "wins": data["wins"],
                "losses": data["losses"],
                "win_rate": round(wr, 1),
            })

        # Backhand: como nao temos campo especifico no modelo Player,
        # retornamos lista vazia (pode ser expandido no futuro)
        backhand_list = []

        age_groups_list = []
        for key, data in by_age_group.items():
            if key == "Desconhecido":
                continue
            total = data["total"]
            wr = (data["wins"] / total * 100) if total > 0 else 0.0
            age_groups_list.append({
                "age_group": key,
                "total": total,
                "wins": data["wins"],
                "losses": data["losses"],
                "win_rate": round(wr, 1),
            })

        return {
            "overall": {
                "total_matches": overall["total_matches"],
                "wins": overall["wins"],
                "losses": overall["losses"],
                "win_rate": round(win_rate, 1),
            },
            "by_type": by_type_list,
            "by_result_type": by_result_type_list,
            "monthly": monthly_list,
            "by_surface": by_surface_list,
            "opponent_profile": {
                "handedness": handedness_list,
                "backhand": backhand_list,
                "age_groups": age_groups_list,
            },
            "streak": streak,
        }

    async def get_monthly(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        months: int = 12,
    ) -> List[Dict[str, Any]]:
        """Retorna apenas dados mensais"""
        dashboard = await self.get_dashboard(db, user_id, months)
        return dashboard["monthly"]

    async def get_breakdown(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Retorna breakdown por tipo de jogo"""
        dashboard = await self.get_dashboard(db, user_id)
        return {
            "by_type": dashboard["by_type"],
            "by_result_type": dashboard["by_result_type"],
        }

    async def get_surface_stats(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> List[Dict[str, Any]]:
        """Retorna estatisticas por superficie"""
        dashboard = await self.get_dashboard(db, user_id)
        return dashboard["by_surface"]

    async def get_opponent_profile(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Retorna estatisticas vs perfil do oponente"""
        dashboard = await self.get_dashboard(db, user_id)
        return dashboard["opponent_profile"]

    async def get_streak(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """Retorna sequencia de resultados"""
        dashboard = await self.get_dashboard(db, user_id)
        return dashboard["streak"][:limit]
