"""
Player Model - Modelo de Jogador

Define a estrutura de dados para representar um jogador de tênis,
incluindo informações pessoais, estatísticas e estado atual na partida.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class PlayerPosition(Enum):
    """Posição do jogador na quadra"""
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


class HandType(Enum):
    """Tipo de empunhadura do jogador"""
    RIGHT_HANDED = "right_handed"
    LEFT_HANDED = "left_handed"


@dataclass
class PlayerInfo:
    """Informações básicas do jogador"""
    name: str
    nationality: str = ""
    birth_date: Optional[datetime] = None
    height: Optional[float] = None  # em metros
    weight: Optional[float] = None  # em kg
    hand_type: HandType = HandType.RIGHT_HANDED
    ranking: Optional[int] = None
    points: Optional[int] = None  # pontos do ranking


@dataclass
class PlayerStats:
    """Estatísticas do jogador durante a partida"""
    # Estatísticas de saque
    aces: int = 0
    first_serve_percentage: float = 0.0
    first_serve_won: int = 0
    second_serve_won: int = 0
    double_faults: int = 0
    service_games_won: int = 0
    break_points_saved: int = 0

    # Estatísticas de retorno
    first_serve_return_won: int = 0
    second_serve_return_won: int = 0
    break_points_converted: int = 0
    return_games_won: int = 0

    # Estatísticas gerais
    winners: int = 0
    unforced_errors: int = 0
    forced_errors: int = 0
    net_points_won: int = 0
    total_points_won: int = 0

    # Movimentação
    distance_covered: float = 0.0  # em metros
    max_speed: float = 0.0  # em km/h
    average_rally_length: float = 0.0


@dataclass
class PlayerPosition2D:
    """Posição 2D do jogador na quadra"""
    x: float
    y: float
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0


@dataclass
class Player:
    """
    Modelo completo de um jogador de tênis.

    Contém todas as informações necessárias para rastrear um jogador
    durante uma partida, incluindo dados pessoais, estatísticas e estado atual.
    """

    # Identificação
    player_id: str
    info: PlayerInfo

    # Estado atual na partida
    position: PlayerPosition = PlayerPosition.LEFT
    current_location: Optional[PlayerPosition2D] = None
    is_serving: bool = False

    # Estatísticas da partida
    stats: PlayerStats = field(default_factory=PlayerStats)

    # Histórico de posições (últimas N posições)
    position_history: List[PlayerPosition2D] = field(default_factory=list)
    max_history_size: int = 100

    # Configurações de detecção
    bbox_color: tuple = (255, 0, 0)  # Cor da caixa delimitadora (BGR)
    track_id: Optional[int] = None  # ID do rastreador SORT

    def update_position(self, x: float, y: float, confidence: float = 1.0):
        """
        Atualiza a posição atual do jogador.

        Args:
            x: Coordenada X na imagem
            y: Coordenada Y na imagem
            confidence: Confiança da detecção (0.0 a 1.0)
        """
        new_position = PlayerPosition2D(x, y, confidence=confidence)
        self.current_location = new_position

        # Adicionar ao histórico
        self.position_history.append(new_position)

        # Manter apenas as últimas N posições
        if len(self.position_history) > self.max_history_size:
            self.position_history.pop(0)

    def get_speed(self) -> float:
        """
        Calcula a velocidade atual do jogador baseada nas duas últimas posições.

        Returns:
            Velocidade em pixels por segundo
        """
        if len(self.position_history) < 2:
            return 0.0

        pos1 = self.position_history[-2]
        pos2 = self.position_history[-1]

        # Calcular distância euclidiana
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        distance = (dx**2 + dy**2)**0.5

        # Calcular tempo decorrido
        time_diff = (pos2.timestamp - pos1.timestamp).total_seconds()

        if time_diff > 0:
            return distance / time_diff
        return 0.0

    def get_average_position(self, last_n: int = 10) -> Optional[PlayerPosition2D]:
        """
        Calcula a posição média das últimas N posições.

        Args:
            last_n: Número de posições a considerar

        Returns:
            Posição média ou None se não houver dados suficientes
        """
        if not self.position_history:
            return None

        recent_positions = self.position_history[-last_n:]

        avg_x = sum(pos.x for pos in recent_positions) / len(recent_positions)
        avg_y = sum(pos.y for pos in recent_positions) / len(recent_positions)
        avg_confidence = sum(pos.confidence for pos in recent_positions) / len(recent_positions)

        return PlayerPosition2D(avg_x, avg_y, confidence=avg_confidence)

    def is_in_service_box(self, court_lines: Dict[str, List[float]]) -> bool:
        """
        Verifica se o jogador está na área de saque.

        Args:
            court_lines: Dicionário com as linhas da quadra

        Returns:
            True se estiver na área de saque
        """
        if not self.current_location:
            return False

        # Implementar lógica de verificação baseada nas linhas da quadra
        # Por enquanto, retorna False como placeholder
        return False

    def update_stats(self, event_type: str, **kwargs):
        """
        Atualiza as estatísticas do jogador baseado em um evento.

        Args:
            event_type: Tipo do evento (ace, winner, error, etc.)
            **kwargs: Parâmetros adicionais do evento
        """
        if event_type == "ace":
            self.stats.aces += 1
        elif event_type == "double_fault":
            self.stats.double_faults += 1
        elif event_type == "winner":
            self.stats.winners += 1
        elif event_type == "unforced_error":
            self.stats.unforced_errors += 1
        elif event_type == "forced_error":
            self.stats.forced_errors += 1
        # Adicionar mais tipos de eventos conforme necessário

    def to_dict(self) -> Dict:
        """
        Converte o jogador para um dicionário.

        Returns:
            Dicionário com todos os dados do jogador
        """
        return {
            'player_id': self.player_id,
            'info': {
                'name': self.info.name,
                'nationality': self.info.nationality,
                'ranking': self.info.ranking,
                'hand_type': self.info.hand_type.value
            },
            'position': self.position.value,
            'current_location': {
                'x': self.current_location.x if self.current_location else None,
                'y': self.current_location.y if self.current_location else None
            } if self.current_location else None,
            'is_serving': self.is_serving,
            'stats': {
                'aces': self.stats.aces,
                'winners': self.stats.winners,
                'unforced_errors': self.stats.unforced_errors,
                'total_points_won': self.stats.total_points_won
            }
        }

    def __str__(self) -> str:
        return f"Player({self.info.name}, {self.position.value})"

    def __repr__(self) -> str:
        return self.__str__()