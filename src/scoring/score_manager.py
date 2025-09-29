"""
Score Manager - Gerenciador de Pontuação

Classe principal para gerenciar a pontuação de uma partida de tênis,
incluindo regras oficiais ATP/WTA, tiebreaks e situações especiais.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging

from .models.scoreboard import Scoreboard, PlayerScoreDisplay, ScoreboardStyle
from .models.point_history import PointHistory, PointDetails, PointOutcome
from ..game_control.models.match import Match


class ScoreManager:
    """
    Gerenciador completo de pontuação para tênis.

    Esta classe implementa todas as regras oficiais de pontuação do tênis
    e fornece interfaces para visualização e análise de dados.
    """

    def __init__(self, match: Match, style: ScoreboardStyle = ScoreboardStyle.TRADITIONAL):
        """
        Inicializa o gerenciador de pontuação.

        Args:
            match: Objeto Match a ser gerenciado
            style: Estilo de visualização do placar
        """
        self.match = match
        self.logger = logging.getLogger(__name__)

        # Inicializar placar
        self.scoreboard = Scoreboard(
            match_id=match.match_id,
            style=style,
            player1=PlayerScoreDisplay(
                name=match.player1.info.name,
                short_name=self._create_short_name(match.player1.info.name),
                ranking=match.player1.info.ranking
            ),
            player2=PlayerScoreDisplay(
                name=match.player2.info.name,
                short_name=self._create_short_name(match.player2.info.name),
                ranking=match.player2.info.ranking
            )
        )

        # Inicializar histórico de pontos
        self.point_history = PointHistory(match_id=match.match_id)

        # Callbacks para eventos de pontuação
        self.score_callbacks: Dict[str, List[Callable]] = {}

        # Cache de estatísticas
        self._stats_cache = {}
        self._cache_timestamp = datetime.now()

        self.logger.info(f"ScoreManager criado para partida {match.match_id}")

    def _create_short_name(self, full_name: str) -> str:
        """
        Cria um nome abreviado para o placar.

        Args:
            full_name: Nome completo do jogador

        Returns:
            Nome abreviado (ex: "R. FEDERER")
        """
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0].upper()
        elif len(parts) == 2:
            return f"{parts[0][0]}. {parts[1].upper()}"
        else:
            # Mais de 2 nomes: primeira inicial + último sobrenome
            return f"{parts[0][0]}. {parts[-1].upper()}"

    def register_score_callback(self, event_type: str, callback: Callable[[Dict], None]):
        """
        Registra um callback para eventos de pontuação.

        Args:
            event_type: Tipo do evento (point_scored, game_won, etc.)
            callback: Função a ser chamada
        """
        if event_type not in self.score_callbacks:
            self.score_callbacks[event_type] = []
        self.score_callbacks[event_type].append(callback)

    def _emit_score_event(self, event_type: str, data: Dict):
        """
        Emite um evento de pontuação.

        Args:
            event_type: Tipo do evento
            data: Dados do evento
        """
        if event_type in self.score_callbacks:
            for callback in self.score_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Erro no callback {event_type}: {e}")

    def update_score(self, winner_player_id: str, point_type: str = "normal", **kwargs):
        """
        Atualiza a pontuação com um novo ponto.

        Args:
            winner_player_id: ID do jogador que ganhou o ponto
            point_type: Tipo do ponto (ace, winner, error, etc.)
            **kwargs: Dados adicionais do ponto
        """
        # Criar detalhes do ponto
        point_details = self._create_point_details(winner_player_id, point_type, **kwargs)

        # Adicionar ao histórico
        self.point_history.add_point(point_details)

        # Atualizar o placar visual
        self.scoreboard.update_from_match(self.match)

        # Limpar cache de estatísticas
        self._invalidate_stats_cache()

        # Emitir evento
        self._emit_score_event('score_updated', {
            'point_details': point_details,
            'current_score': self.get_current_score()
        })

        self.logger.debug(f"Pontuação atualizada: {point_type} para {winner_player_id}")

    def _create_point_details(self, winner_player_id: str, point_type: str, **kwargs) -> PointDetails:
        """
        Cria um objeto PointDetails com as informações do ponto.

        Args:
            winner_player_id: ID do jogador que ganhou o ponto
            point_type: Tipo do ponto
            **kwargs: Dados adicionais

        Returns:
            Objeto PointDetails preenchido
        """
        # Mapear tipo do ponto para PointOutcome
        outcome_map = {
            'ace': PointOutcome.ACE,
            'winner': PointOutcome.WINNER,
            'unforced_error': PointOutcome.UNFORCED_ERROR,
            'forced_error': PointOutcome.FORCED_ERROR,
            'double_fault': PointOutcome.DOUBLE_FAULT,
            'service_winner': PointOutcome.SERVICE_WINNER,
            'return_winner': PointOutcome.RETURN_WINNER
        }

        outcome = outcome_map.get(point_type, PointOutcome.WINNER)

        return PointDetails(
            point_id=f"{self.match.match_id}_{len(self.point_history.points) + 1}",
            match_id=self.match.match_id,
            timestamp=datetime.now(),
            set_number=self.match.current_set,
            game_number=self.match.current_game,
            point_number=self.match.current_point,
            score_before=self.match._get_current_score(),
            serving_player_id=self.match.serving_player,
            winner_player_id=winner_player_id,
            outcome=outcome,
            is_break_point=self._is_break_point(),
            is_set_point=self._is_set_point(),
            is_match_point=self._is_match_point(),
            is_deuce=self.match.current_game_score.is_deuce,
            game_situation=self._get_game_situation(),
            **kwargs
        )

    def _is_break_point(self) -> bool:
        """Verifica se é um break point"""
        serving_player = self.match.serving_player
        game = self.match.current_game_score

        if serving_player == self.match.player1.player_id:
            # Player 1 sacando, player 2 pode quebrar
            return (game.player2_points == 40 and game.player1_points < 40) or \
                   (game.has_advantage == self.match.player2.player_id)
        else:
            # Player 2 sacando, player 1 pode quebrar
            return (game.player1_points == 40 and game.player2_points < 40) or \
                   (game.has_advantage == self.match.player1.player_id)

    def _is_set_point(self) -> bool:
        """Verifica se é um set point"""
        current_set = self.match.current_set_score
        p1_games = current_set.player1_games
        p2_games = current_set.player2_games

        # Verificar se algum jogador pode ganhar o set no próximo game
        if p1_games >= 5 and p1_games > p2_games:
            return True
        if p2_games >= 5 and p2_games > p1_games:
            return True

        # Verificar tiebreak
        if current_set.is_tiebreak:
            tb1 = current_set.player1_tiebreak
            tb2 = current_set.player2_tiebreak
            return (tb1 >= 6 and tb1 > tb2) or (tb2 >= 6 and tb2 > tb1)

        return False

    def _is_match_point(self) -> bool:
        """Verifica se é um match point"""
        # Contar sets ganhos
        sets_p1 = sum(1 for s in self.match.sets if s.winner == self.match.player1.player_id)
        sets_p2 = sum(1 for s in self.match.sets if s.winner == self.match.player2.player_id)

        sets_needed = 2 if self.match.match_format.value == 'best_of_3' else 3

        # Verificar se algum jogador está a um set da vitória e é set point
        if (sets_p1 == sets_needed - 1 or sets_p2 == sets_needed - 1) and self._is_set_point():
            return True

        return False

    def _get_game_situation(self) -> str:
        """Retorna a situação atual do game como string"""
        if self.match.current_set_score.is_tiebreak:
            tb1 = self.match.current_set_score.player1_tiebreak
            tb2 = self.match.current_set_score.player2_tiebreak
            return f"TB: {tb1}-{tb2}"

        game = self.match.current_game_score
        point_map = {0: "0", 15: "15", 30: "30", 40: "40"}

        if game.is_deuce:
            if game.has_advantage == self.match.player1.player_id:
                return "AD-40"
            elif game.has_advantage == self.match.player2.player_id:
                return "40-AD"
            else:
                return "40-40"

        p1_str = point_map.get(game.player1_points, str(game.player1_points))
        p2_str = point_map.get(game.player2_points, str(game.player2_points))

        return f"{p1_str}-{p2_str}"

    def get_current_score(self) -> Dict:
        """
        Retorna a pontuação atual formatada.

        Returns:
            Dicionário com pontuação atual
        """
        return self.scoreboard.get_score_for_broadcast()

    def get_live_score_data(self) -> Dict:
        """
        Retorna dados otimizados para transmissão ao vivo.

        Returns:
            Dados formatados para live streaming
        """
        return {
            'scoreboard': self.scoreboard.to_dict(),
            'last_points': self.get_recent_points(5),
            'key_stats': self.get_key_statistics(),
            'situation': {
                'is_break_point': self._is_break_point(),
                'is_set_point': self._is_set_point(),
                'is_match_point': self._is_match_point(),
                'serving_player': self.match.serving_player
            }
        }

    def get_recent_points(self, limit: int = 10) -> List[Dict]:
        """
        Retorna os pontos mais recentes.

        Args:
            limit: Número de pontos a retornar

        Returns:
            Lista com os pontos mais recentes
        """
        recent_points = self.point_history.points[-limit:] if self.point_history.points else []

        return [
            {
                'point_id': p.point_id,
                'timestamp': p.timestamp.isoformat(),
                'winner_player_id': p.winner_player_id,
                'outcome': p.outcome.value,
                'score_after': p.score_after,
                'is_break_point': p.is_break_point,
                'is_set_point': p.is_set_point,
                'is_match_point': p.is_match_point
            }
            for p in recent_points
        ]

    def get_key_statistics(self) -> Dict:
        """
        Retorna estatísticas principais para exibição.

        Returns:
            Estatísticas principais da partida
        """
        if self._is_stats_cache_valid():
            return self._stats_cache

        # Calcular estatísticas
        p1_points = self.point_history.get_points_by_player(self.match.player1.player_id)
        p2_points = self.point_history.get_points_by_player(self.match.player2.player_id)

        # Aces
        p1_aces = len([p for p in p1_points if p.outcome == PointOutcome.ACE])
        p2_aces = len([p for p in p2_points if p.outcome == PointOutcome.ACE])

        # Winners
        p1_winners = len([p for p in p1_points if p.outcome == PointOutcome.WINNER])
        p2_winners = len([p for p in p2_points if p.outcome == PointOutcome.WINNER])

        # Erros não forçados
        p1_ue = len([p for p in p1_points if p.outcome == PointOutcome.UNFORCED_ERROR])
        p2_ue = len([p for p in p2_points if p.outcome == PointOutcome.UNFORCED_ERROR])

        # Break points
        break_points = self.point_history.get_break_points()
        p1_bp_won = len([p for p in break_points if p.winner_player_id == self.match.player1.player_id])
        p2_bp_won = len([p for p in break_points if p.winner_player_id == self.match.player2.player_id])

        self._stats_cache = {
            'player1': {
                'aces': p1_aces,
                'winners': p1_winners,
                'unforced_errors': p1_ue,
                'points_won': len(p1_points),
                'break_points_won': p1_bp_won
            },
            'player2': {
                'aces': p2_aces,
                'winners': p2_winners,
                'unforced_errors': p2_ue,
                'points_won': len(p2_points),
                'break_points_won': p2_bp_won
            },
            'match': {
                'total_points': len(self.point_history.points),
                'total_break_points': len(break_points),
                'longest_rally': max([r.rally_length for r in self.point_history.rallies], default=0)
            }
        }

        self._cache_timestamp = datetime.now()
        return self._stats_cache

    def _is_stats_cache_valid(self) -> bool:
        """Verifica se o cache de estatísticas ainda é válido"""
        return (datetime.now() - self._cache_timestamp).seconds < 30

    def _invalidate_stats_cache(self):
        """Invalida o cache de estatísticas"""
        self._stats_cache = {}

    def get_set_statistics(self, set_number: int) -> Dict:
        """
        Retorna estatísticas de um set específico.

        Args:
            set_number: Número do set

        Returns:
            Estatísticas do set
        """
        set_points = self.point_history.get_points_by_set(set_number)

        if not set_points:
            return {}

        p1_points = [p for p in set_points if p.winner_player_id == self.match.player1.player_id]
        p2_points = [p for p in set_points if p.winner_player_id == self.match.player2.player_id]

        return {
            'set_number': set_number,
            'total_points': len(set_points),
            'player1_points': len(p1_points),
            'player2_points': len(p2_points),
            'duration': self._calculate_set_duration(set_points),
            'key_moments': self._get_set_key_moments(set_points)
        }

    def _calculate_set_duration(self, set_points: List[PointDetails]) -> str:
        """Calcula a duração de um set"""
        if not set_points:
            return "0:00"

        start_time = set_points[0].timestamp
        end_time = set_points[-1].timestamp
        duration = end_time - start_time

        minutes = duration.total_seconds() // 60
        return f"{int(minutes):02d}:{int(duration.total_seconds() % 60):02d}"

    def _get_set_key_moments(self, set_points: List[PointDetails]) -> List[Dict]:
        """Encontra momentos-chave de um set"""
        key_moments = []

        for point in set_points:
            if point.is_break_point or point.is_set_point or point.outcome == PointOutcome.ACE:
                key_moments.append({
                    'timestamp': point.timestamp.isoformat(),
                    'type': 'break_point' if point.is_break_point else 'set_point' if point.is_set_point else 'ace',
                    'player_id': point.winner_player_id,
                    'description': f"{point.outcome.value} by {point.winner_player_id}"
                })

        return key_moments

    def export_scoring_data(self) -> Dict:
        """
        Exporta todos os dados de pontuação.

        Returns:
            Dados completos de pontuação
        """
        return {
            'scoreboard': self.scoreboard.to_dict(),
            'point_history': self.point_history.to_dict(),
            'statistics': self.get_key_statistics(),
            'export_timestamp': datetime.now().isoformat()
        }

    def __str__(self) -> str:
        return f"ScoreManager({self.match.match_id}: {self.scoreboard.get_score_for_broadcast()['score']})"

    def __repr__(self) -> str:
        return self.__str__()