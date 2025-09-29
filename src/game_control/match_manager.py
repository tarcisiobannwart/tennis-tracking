"""
Match Manager - Gerenciador de Partidas

Classe principal para gerenciar uma partida de tênis, coordenando
todos os aspectos do jogo incluindo pontuação, eventos e estatísticas.
"""

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import logging

from .models.match import Match, MatchStatus, MatchType, MatchFormat
from .models.player import Player, PlayerInfo
from .models.court import Court


class MatchManager:
    """
    Gerenciador principal de uma partida de tênis.

    Esta classe coordena todos os aspectos de uma partida em tempo real:
    - Controle de pontuação
    - Registro de eventos
    - Atualização de estatísticas
    - Notificações de estado
    """

    def __init__(self, match_id: str, player1_info: PlayerInfo, player2_info: PlayerInfo,
                 court: Court, match_format: MatchFormat = MatchFormat.BEST_OF_3):
        """
        Inicializa o gerenciador de partida.

        Args:
            match_id: Identificador único da partida
            player1_info: Informações do jogador 1
            player2_info: Informações do jogador 2
            court: Quadra da partida
            match_format: Formato da partida (melhor de 3 ou 5)
        """
        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Criar jogadores
        player1 = Player(player_id="player1", info=player1_info)
        player2 = Player(player_id="player2", info=player2_info)

        # Criar partida
        self.match = Match(
            match_id=match_id,
            player1=player1,
            player2=player2,
            court=court,
            match_format=match_format
        )

        # Callbacks para eventos
        self.event_callbacks: Dict[str, List[Callable]] = {}

        # Estado interno
        self.is_paused = False
        self.last_update = datetime.now()

        self.logger.info(f"MatchManager criado para partida {match_id}")

    def register_event_callback(self, event_type: str, callback: Callable[[Dict], None]):
        """
        Registra um callback para ser chamado quando um evento específico ocorrer.

        Args:
            event_type: Tipo do evento (point_scored, game_won, set_won, etc.)
            callback: Função a ser chamada com os dados do evento
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)

    def _emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Emite um evento para todos os callbacks registrados.

        Args:
            event_type: Tipo do evento
            event_data: Dados do evento
        """
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Erro no callback {event_type}: {e}")

    def start_match(self, serving_player_id: str = "player1", tournament_name: str = "",
                   round_name: str = ""):
        """
        Inicia a partida.

        Args:
            serving_player_id: ID do jogador que vai sacar primeiro
            tournament_name: Nome do torneio
            round_name: Nome da rodada
        """
        if self.match.status != MatchStatus.NOT_STARTED:
            raise ValueError(f"Partida já iniciada. Status atual: {self.match.status}")

        self.match.tournament_name = tournament_name
        self.match.round_name = round_name
        self.match.start_match(serving_player_id)

        event_data = {
            'match_id': self.match.match_id,
            'serving_player': serving_player_id,
            'timestamp': datetime.now().isoformat()
        }
        self._emit_event('match_started', event_data)

        self.logger.info(f"Partida {self.match.match_id} iniciada")

    def add_point(self, winner_player_id: str, point_type: str = "normal",
                  ball_speed: Optional[float] = None, ball_position: Optional[tuple] = None,
                  shot_type: Optional[str] = None, **kwargs):
        """
        Adiciona um ponto para um jogador.

        Args:
            winner_player_id: ID do jogador que ganhou o ponto
            point_type: Tipo do ponto (ace, winner, error, fault, etc.)
            ball_speed: Velocidade da bola (se disponível)
            ball_position: Posição da bola (se disponível)
            shot_type: Tipo do golpe (forehand, backhand, serve, etc.)
            **kwargs: Dados adicionais do ponto
        """
        if self.match.status != MatchStatus.IN_PROGRESS:
            raise ValueError(f"Partida não está em andamento. Status: {self.match.status}")

        if self.is_paused:
            self.logger.warning("Tentativa de adicionar ponto com partida pausada")
            return

        # Preparar dados adicionais
        point_data = {
            'ball_speed': ball_speed,
            'ball_position': ball_position,
            'shot_type': shot_type,
            **kwargs
        }

        # Salvar estado antes do ponto
        score_before = self.match._get_current_score()

        # Adicionar ponto
        self.match.add_point(winner_player_id, point_type, **point_data)

        # Emitir eventos baseados no que aconteceu
        self._emit_point_events(winner_player_id, point_type, score_before, point_data)

        self.last_update = datetime.now()
        self.logger.debug(f"Ponto adicionado: {point_type} para {winner_player_id}")

    def _emit_point_events(self, winner_player_id: str, point_type: str,
                          score_before: Dict, point_data: Dict):
        """
        Emite eventos relacionados ao ponto marcado.

        Args:
            winner_player_id: ID do jogador que ganhou o ponto
            point_type: Tipo do ponto
            score_before: Pontuação antes do ponto
            point_data: Dados adicionais do ponto
        """
        # Evento básico de ponto
        event_data = {
            'match_id': self.match.match_id,
            'winner_player_id': winner_player_id,
            'point_type': point_type,
            'score_before': score_before,
            'score_after': self.match._get_current_score(),
            'point_data': point_data,
            'timestamp': datetime.now().isoformat()
        }
        self._emit_event('point_scored', event_data)

        # Verificar se o game foi ganho
        if self.match.current_game_score.is_completed:
            game_event = {
                'match_id': self.match.match_id,
                'winner_player_id': self.match.current_game_score.winner,
                'set_number': self.match.current_set,
                'game_number': self.match.current_game,
                'timestamp': datetime.now().isoformat()
            }
            self._emit_event('game_won', game_event)

            # Verificar se o set foi ganho
            if self.match.current_set_score.is_completed:
                set_event = {
                    'match_id': self.match.match_id,
                    'winner_player_id': self.match.current_set_score.winner,
                    'set_number': self.match.current_set,
                    'timestamp': datetime.now().isoformat()
                }
                self._emit_event('set_won', set_event)

                # Verificar se a partida terminou
                if self.match.status == MatchStatus.COMPLETED:
                    match_event = {
                        'match_id': self.match.match_id,
                        'winner_player_id': self.match._get_match_winner(),
                        'duration': self._get_match_duration(),
                        'timestamp': datetime.now().isoformat()
                    }
                    self._emit_event('match_completed', match_event)

        # Eventos especiais por tipo de ponto
        if point_type == "ace":
            self._emit_event('ace', event_data)
        elif point_type == "winner":
            self._emit_event('winner', event_data)
        elif point_type == "double_fault":
            self._emit_event('double_fault', event_data)

    def pause_match(self):
        """Pausa a partida."""
        self.is_paused = True
        event_data = {
            'match_id': self.match.match_id,
            'timestamp': datetime.now().isoformat()
        }
        self._emit_event('match_paused', event_data)
        self.logger.info(f"Partida {self.match.match_id} pausada")

    def resume_match(self):
        """Resume a partida."""
        self.is_paused = False
        event_data = {
            'match_id': self.match.match_id,
            'timestamp': datetime.now().isoformat()
        }
        self._emit_event('match_resumed', event_data)
        self.logger.info(f"Partida {self.match.match_id} resumida")

    def update_player_position(self, player_id: str, x: float, y: float, confidence: float = 1.0):
        """
        Atualiza a posição de um jogador na quadra.

        Args:
            player_id: ID do jogador
            x: Coordenada X
            y: Coordenada Y
            confidence: Confiança da detecção
        """
        player = self.match.player1 if player_id == self.match.player1.player_id else self.match.player2
        player.update_position(x, y, confidence)

    def get_current_score(self) -> Dict:
        """
        Retorna a pontuação atual da partida.

        Returns:
            Dicionário com a pontuação atual
        """
        return self.match._get_current_score()

    def get_score_string(self) -> str:
        """
        Retorna a pontuação atual como string formatada.

        Returns:
            String com a pontuação atual
        """
        return self.match.get_score_string()

    def get_match_statistics(self) -> Dict:
        """
        Retorna estatísticas completas da partida.

        Returns:
            Dicionário com estatísticas detalhadas
        """
        return {
            'match_info': {
                'match_id': self.match.match_id,
                'tournament': self.match.tournament_name,
                'round': self.match.round_name,
                'status': self.match.status.value,
                'duration': self._get_match_duration()
            },
            'players': {
                'player1': {
                    'info': self.match.player1.info.__dict__,
                    'stats': self.match.player1.stats.__dict__
                },
                'player2': {
                    'info': self.match.player2.info.__dict__,
                    'stats': self.match.player2.stats.__dict__
                }
            },
            'score': self.get_current_score(),
            'events_count': len(self.match.events)
        }

    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """
        Retorna os eventos mais recentes da partida.

        Args:
            limit: Número máximo de eventos a retornar

        Returns:
            Lista com os eventos mais recentes
        """
        recent_events = self.match.events[-limit:] if self.match.events else []
        return [
            {
                'event_id': event.event_id,
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type,
                'player_id': event.player_id,
                'description': event.description,
                'set_number': event.set_number,
                'game_number': event.game_number
            }
            for event in recent_events
        ]

    def _get_match_duration(self) -> Optional[str]:
        """
        Calcula a duração da partida.

        Returns:
            String com a duração da partida ou None se não iniciada
        """
        if not self.match.start_time:
            return None

        end_time = self.match.end_time or datetime.now()
        duration = end_time - self.match.start_time

        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def export_match_data(self) -> Dict:
        """
        Exporta todos os dados da partida.

        Returns:
            Dicionário completo com todos os dados da partida
        """
        return {
            'match': self.match.to_dict(),
            'events': [
                {
                    'event_id': event.event_id,
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type,
                    'player_id': event.player_id,
                    'description': event.description,
                    'set_number': event.set_number,
                    'game_number': event.game_number,
                    'point_number': event.point_number,
                    'additional_data': event.additional_data
                }
                for event in self.match.events
            ],
            'statistics': self.get_match_statistics()
        }

    def is_break_point(self) -> bool:
        """
        Verifica se é um break point.

        Returns:
            True se for break point
        """
        # Verificar se o jogador que não está sacando pode ganhar o game
        serving_player = self.match.serving_player
        game_score = self.match.current_game_score

        if serving_player == self.match.player1.player_id:
            # Player 1 está sacando, player 2 pode fazer o break
            if game_score.player2_points == 40 and game_score.player1_points < 40:
                return True
            if game_score.has_advantage == self.match.player2.player_id:
                return True
        else:
            # Player 2 está sacando, player 1 pode fazer o break
            if game_score.player1_points == 40 and game_score.player2_points < 40:
                return True
            if game_score.has_advantage == self.match.player1.player_id:
                return True

        return False

    def is_match_point(self) -> bool:
        """
        Verifica se é um match point.

        Returns:
            True se for match point
        """
        # Implementar lógica de match point baseada no formato da partida
        # Por enquanto, retorna False como placeholder
        return False

    def __str__(self) -> str:
        return f"MatchManager({self.match.match_id}: {self.get_score_string()})"

    def __repr__(self) -> str:
        return self.__str__()