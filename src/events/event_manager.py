"""
Event Manager - Gerenciador de Eventos

Gerencia eventos de tênis em tempo real, incluindo detecção automática
de aces, winners, erros e situações especiais.
"""

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import logging
from enum import Enum

from ..game_control.models.match import Match


class EventType(Enum):
    """Tipos de eventos de tênis"""
    # Eventos de ponto
    ACE = "ace"
    WINNER = "winner"
    UNFORCED_ERROR = "unforced_error"
    FORCED_ERROR = "forced_error"
    DOUBLE_FAULT = "double_fault"
    SERVICE_WINNER = "service_winner"
    RETURN_WINNER = "return_winner"

    # Eventos de jogo
    BREAK_POINT = "break_point"
    BREAK_POINT_SAVED = "break_point_saved"
    BREAK_POINT_CONVERTED = "break_point_converted"
    GAME_WON = "game_won"
    SET_WON = "set_won"
    MATCH_WON = "match_won"

    # Eventos especiais
    DEUCE = "deuce"
    ADVANTAGE = "advantage"
    TIEBREAK_START = "tiebreak_start"
    TIEBREAK_END = "tiebreak_end"

    # Eventos técnicos
    CHALLENGE = "challenge"
    CHALLENGE_SUCCESSFUL = "challenge_successful"
    CHALLENGE_UNSUCCESSFUL = "challenge_unsuccessful"
    TIME_VIOLATION = "time_violation"
    MEDICAL_TIMEOUT = "medical_timeout"


class EventPriority(Enum):
    """Prioridade dos eventos"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TennisEvent:
    """Representa um evento de tênis"""

    def __init__(self, event_type: EventType, player_id: str,
                 priority: EventPriority = EventPriority.NORMAL,
                 description: str = "", **kwargs):
        self.event_id = f"event_{int(datetime.now().timestamp() * 1000)}"
        self.event_type = event_type
        self.player_id = player_id
        self.priority = priority
        self.timestamp = datetime.now()
        self.description = description
        self.data = kwargs

    def to_dict(self) -> Dict:
        """Converte evento para dicionário"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'player_id': self.player_id,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'data': self.data
        }


class EventManager:
    """
    Gerenciador de eventos de tênis.

    Detecta, processa e distribui eventos durante uma partida.
    """

    def __init__(self, match: Match):
        """
        Inicializa o gerenciador de eventos.

        Args:
            match: Partida a ser monitorada
        """
        self.match = match
        self.logger = logging.getLogger(__name__)

        # Histórico de eventos
        self.events: List[TennisEvent] = []

        # Callbacks para diferentes tipos de eventos
        self.event_callbacks: Dict[EventType, List[Callable]] = {}

        # Estado interno para detecção de eventos
        self._last_game_score = None
        self._last_set_score = None
        self._break_point_active = False
        self._deuce_active = False

        # Configurações
        self.auto_detection = True
        self.event_threshold = {
            'ace_speed': 120,  # km/h mínimo para considerar ace
            'winner_angle': 30,  # graus para considerar winner
        }

        self.logger.info(f"EventManager criado para partida {match.match_id}")

    def register_event_callback(self, event_type: EventType, callback: Callable[[TennisEvent], None]):
        """
        Registra callback para um tipo de evento.

        Args:
            event_type: Tipo do evento
            callback: Função a ser chamada quando o evento ocorrer
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []

        self.event_callbacks[event_type].append(callback)
        self.logger.debug(f"Callback registrado para {event_type.value}")

    def emit_event(self, event_type: EventType, player_id: str,
                   priority: EventPriority = EventPriority.NORMAL,
                   description: str = "", **kwargs):
        """
        Emite um evento.

        Args:
            event_type: Tipo do evento
            player_id: ID do jogador relacionado
            priority: Prioridade do evento
            description: Descrição do evento
            **kwargs: Dados adicionais
        """
        # Criar evento
        event = TennisEvent(
            event_type=event_type,
            player_id=player_id,
            priority=priority,
            description=description,
            **kwargs
        )

        # Adicionar ao histórico
        self.events.append(event)

        # Executar callbacks
        self._execute_callbacks(event)

        # Log do evento
        self.logger.info(f"Evento emitido: {event_type.value} - {player_id} - {description}")

    def _execute_callbacks(self, event: TennisEvent):
        """
        Executa callbacks para um evento.

        Args:
            event: Evento a ser processado
        """
        if event.event_type in self.event_callbacks:
            for callback in self.event_callbacks[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Erro no callback {event.event_type.value}: {e}")

    def analyze_point(self, point_type: str, winner_player_id: str, **point_data):
        """
        Analisa um ponto e detecta eventos automaticamente.

        Args:
            point_type: Tipo do ponto
            winner_player_id: ID do jogador que ganhou o ponto
            **point_data: Dados adicionais do ponto
        """
        if not self.auto_detection:
            return

        # Detectar tipo de evento baseado no ponto
        event_type = self._classify_point_event(point_type, point_data)

        if event_type:
            description = self._generate_event_description(event_type, winner_player_id, point_data)
            priority = self._get_event_priority(event_type)

            self.emit_event(
                event_type=event_type,
                player_id=winner_player_id,
                priority=priority,
                description=description,
                **point_data
            )

        # Detectar eventos situacionais
        self._detect_situational_events(winner_player_id)

    def _classify_point_event(self, point_type: str, point_data: Dict) -> Optional[EventType]:
        """
        Classifica o tipo de evento baseado no ponto.

        Args:
            point_type: Tipo do ponto
            point_data: Dados do ponto

        Returns:
            Tipo de evento ou None
        """
        type_mapping = {
            'ace': EventType.ACE,
            'winner': EventType.WINNER,
            'unforced_error': EventType.UNFORCED_ERROR,
            'forced_error': EventType.FORCED_ERROR,
            'double_fault': EventType.DOUBLE_FAULT,
            'service_winner': EventType.SERVICE_WINNER,
            'return_winner': EventType.RETURN_WINNER
        }

        return type_mapping.get(point_type)

    def _generate_event_description(self, event_type: EventType, player_id: str, point_data: Dict) -> str:
        """
        Gera descrição para um evento.

        Args:
            event_type: Tipo do evento
            player_id: ID do jogador
            point_data: Dados do ponto

        Returns:
            Descrição do evento
        """
        player_name = self._get_player_name(player_id)

        descriptions = {
            EventType.ACE: f"Ace de {player_name}",
            EventType.WINNER: f"Winner de {player_name}",
            EventType.UNFORCED_ERROR: f"Erro não forçado de {player_name}",
            EventType.DOUBLE_FAULT: f"Dupla falta de {player_name}",
            EventType.SERVICE_WINNER: f"Saque vencedor de {player_name}",
            EventType.RETURN_WINNER: f"Devolução vencedora de {player_name}"
        }

        base_description = descriptions.get(event_type, f"Evento de {player_name}")

        # Adicionar dados específicos
        if 'ball_speed' in point_data and point_data['ball_speed']:
            base_description += f" ({point_data['ball_speed']:.1f} km/h)"

        return base_description

    def _get_event_priority(self, event_type: EventType) -> EventPriority:
        """
        Determina a prioridade de um evento.

        Args:
            event_type: Tipo do evento

        Returns:
            Prioridade do evento
        """
        high_priority_events = {
            EventType.ACE,
            EventType.BREAK_POINT_CONVERTED,
            EventType.SET_WON,
            EventType.MATCH_WON
        }

        critical_priority_events = {
            EventType.MATCH_WON
        }

        if event_type in critical_priority_events:
            return EventPriority.CRITICAL
        elif event_type in high_priority_events:
            return EventPriority.HIGH
        else:
            return EventPriority.NORMAL

    def _detect_situational_events(self, winner_player_id: str):
        """
        Detecta eventos situacionais (break points, deuce, etc.).

        Args:
            winner_player_id: ID do jogador que ganhou o ponto
        """
        # Detectar break point
        if self._is_break_point_situation():
            if not self._break_point_active:
                self.emit_event(
                    EventType.BREAK_POINT,
                    winner_player_id,
                    EventPriority.HIGH,
                    "Break point"
                )
                self._break_point_active = True

        # Detectar deuce
        if self._is_deuce_situation():
            if not self._deuce_active:
                self.emit_event(
                    EventType.DEUCE,
                    winner_player_id,
                    EventPriority.NORMAL,
                    "Deuce"
                )
                self._deuce_active = True
        else:
            self._deuce_active = False

        # Detectar vantagem
        advantage_player = self._get_advantage_player()
        if advantage_player:
            self.emit_event(
                EventType.ADVANTAGE,
                advantage_player,
                EventPriority.NORMAL,
                f"Vantagem para {self._get_player_name(advantage_player)}"
            )

    def _is_break_point_situation(self) -> bool:
        """Verifica se é uma situação de break point"""
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

    def _is_deuce_situation(self) -> bool:
        """Verifica se é deuce"""
        return self.match.current_game_score.is_deuce

    def _get_advantage_player(self) -> Optional[str]:
        """Retorna o jogador com vantagem"""
        return self.match.current_game_score.has_advantage

    def _get_player_name(self, player_id: str) -> str:
        """Retorna o nome do jogador"""
        if player_id == self.match.player1.player_id:
            return self.match.player1.info.name
        else:
            return self.match.player2.info.name

    def get_recent_events(self, limit: int = 10, event_type: Optional[EventType] = None) -> List[Dict]:
        """
        Retorna eventos recentes.

        Args:
            limit: Número máximo de eventos
            event_type: Filtrar por tipo de evento

        Returns:
            Lista de eventos recentes
        """
        events = self.events

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Ordenar por timestamp (mais recente primeiro)
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)

        return [event.to_dict() for event in events[:limit]]

    def get_event_statistics(self) -> Dict:
        """
        Retorna estatísticas dos eventos.

        Returns:
            Estatísticas dos eventos
        """
        if not self.events:
            return {}

        # Contar eventos por tipo
        event_counts = {}
        for event in self.events:
            event_type = event.event_type.value
            if event_type not in event_counts:
                event_counts[event_type] = 0
            event_counts[event_type] += 1

        # Contar eventos por jogador
        player_events = {}
        for event in self.events:
            player_id = event.player_id
            if player_id not in player_events:
                player_events[player_id] = 0
            player_events[player_id] += 1

        # Eventos de alta prioridade
        high_priority_events = [
            e for e in self.events
            if e.priority in [EventPriority.HIGH, EventPriority.CRITICAL]
        ]

        return {
            'total_events': len(self.events),
            'events_by_type': event_counts,
            'events_by_player': player_events,
            'high_priority_events': len(high_priority_events),
            'events_per_minute': self._calculate_events_per_minute()
        }

    def _calculate_events_per_minute(self) -> float:
        """Calcula eventos por minuto"""
        if not self.events or not self.match.start_time:
            return 0.0

        duration = datetime.now() - self.match.start_time
        minutes = duration.total_seconds() / 60

        if minutes == 0:
            return 0.0

        return len(self.events) / minutes

    def export_events(self) -> Dict:
        """
        Exporta todos os eventos.

        Returns:
            Dados completos dos eventos
        """
        return {
            'match_id': self.match.match_id,
            'export_timestamp': datetime.now().isoformat(),
            'total_events': len(self.events),
            'events': [event.to_dict() for event in self.events],
            'statistics': self.get_event_statistics()
        }

    def clear_events(self):
        """Limpa o histórico de eventos"""
        self.events.clear()
        self._break_point_active = False
        self._deuce_active = False

    def __str__(self) -> str:
        return f"EventManager({self.match.match_id}: {len(self.events)} events)"

    def __repr__(self) -> str:
        return self.__str__()