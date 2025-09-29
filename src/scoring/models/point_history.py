"""
Point History Model - Modelo de Histórico de Pontos

Armazena o histórico detalhado de cada ponto da partida
para análise posterior e replay.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class PointOutcome(Enum):
    """Resultado de um ponto"""
    ACE = "ace"
    WINNER = "winner"
    FORCED_ERROR = "forced_error"
    UNFORCED_ERROR = "unforced_error"
    DOUBLE_FAULT = "double_fault"
    FAULT = "fault"
    SERVICE_WINNER = "service_winner"
    RETURN_WINNER = "return_winner"


class ShotType(Enum):
    """Tipos de golpe"""
    SERVE = "serve"
    FOREHAND = "forehand"
    BACKHAND = "backhand"
    VOLLEY = "volley"
    SMASH = "smash"
    DROP_SHOT = "drop_shot"
    LOB = "lob"
    SLICE = "slice"
    RETURN = "return"


class CourtZone(Enum):
    """Zonas da quadra"""
    SERVICE_BOX_AD = "service_box_ad"          # Área de saque lado esquerdo
    SERVICE_BOX_DEUCE = "service_box_deuce"    # Área de saque lado direito
    BACKCOURT_AD = "backcourt_ad"              # Fundo esquerdo
    BACKCOURT_DEUCE = "backcourt_deuce"        # Fundo direito
    NET_AREA = "net_area"                      # Área próxima à rede
    WIDE_AD = "wide_ad"                        # Fora da quadra esquerda
    WIDE_DEUCE = "wide_deuce"                  # Fora da quadra direita
    LONG = "long"                              # Longo (além da linha de base)


@dataclass
class BallPosition:
    """Posição da bola em um momento específico"""
    x: float                    # Coordenada X (pixels ou metros)
    y: float                    # Coordenada Y (pixels ou metros)
    timestamp: datetime         # Momento da detecção
    confidence: float = 1.0     # Confiança da detecção
    speed: Optional[float] = None        # Velocidade neste ponto
    height: Optional[float] = None       # Altura estimada
    zone: Optional[CourtZone] = None     # Zona da quadra


@dataclass
class Shot:
    """Informações de um golpe"""
    shot_id: str
    player_id: str
    shot_type: ShotType
    ball_position: BallPosition
    contact_point: Optional[Tuple[float, float]] = None  # Ponto de contato
    ball_speed: Optional[float] = None                   # Velocidade da bola
    spin_rate: Optional[float] = None                    # Taxa de rotação
    angle: Optional[float] = None                        # Ângulo do golpe
    power: Optional[float] = None                        # Potência (0-100)
    placement_quality: Optional[float] = None            # Qualidade do posicionamento


@dataclass
class Rally:
    """Sequência de golpes em um rally"""
    rally_id: str
    start_time: datetime
    end_time: datetime
    shots: List[Shot] = field(default_factory=list)
    rally_length: int = 0                # Número de golpes
    duration: float = 0.0                # Duração em segundos
    winner_player_id: Optional[str] = None
    ending_shot: Optional[Shot] = None
    max_speed: float = 0.0
    avg_speed: float = 0.0


@dataclass
class PointDetails:
    """Detalhes completos de um ponto"""
    point_id: str
    match_id: str
    timestamp: datetime

    # Contexto do ponto
    set_number: int
    game_number: int
    point_number: int
    score_before: Dict[str, any]
    score_after: Dict[str, any]

    # Servidor
    serving_player_id: str
    service_number: int = 1              # 1º ou 2º saque
    service_zone: Optional[CourtZone] = None

    # Resultado
    winner_player_id: str
    outcome: PointOutcome
    ending_shot_type: Optional[ShotType] = None

    # Rally
    rally: Optional[Rally] = None
    ball_trajectory: List[BallPosition] = field(default_factory=list)

    # Contexto situacional
    is_break_point: bool = False
    is_set_point: bool = False
    is_match_point: bool = False
    is_deuce: bool = False
    game_situation: str = ""             # "15-30", "40-AD", etc.

    # Estatísticas do ponto
    duration: float = 0.0                # Duração total do ponto
    distance_covered_p1: float = 0.0     # Distância percorrida pelo player 1
    distance_covered_p2: float = 0.0     # Distância percorrida pelo player 2
    max_rally_speed: float = 0.0
    avg_rally_speed: float = 0.0

    # Dados adicionais
    weather_conditions: Optional[Dict] = None
    court_conditions: Optional[str] = None
    additional_notes: str = ""


@dataclass
class PointHistory:
    """
    Histórico completo de pontos de uma partida.

    Armazena todos os pontos com detalhes completos para análise
    e geração de relatórios estatísticos.
    """

    match_id: str
    points: List[PointDetails] = field(default_factory=list)
    rallies: List[Rally] = field(default_factory=list)

    # Índices para busca rápida
    _points_by_set: Dict[int, List[PointDetails]] = field(default_factory=dict, init=False)
    _points_by_player: Dict[str, List[PointDetails]] = field(default_factory=dict, init=False)
    _points_by_outcome: Dict[PointOutcome, List[PointDetails]] = field(default_factory=dict, init=False)

    def __post_init__(self):
        """Inicialização após criação"""
        self._rebuild_indices()

    def add_point(self, point: PointDetails):
        """
        Adiciona um ponto ao histórico.

        Args:
            point: Detalhes do ponto a ser adicionado
        """
        self.points.append(point)

        # Adicionar rally se existir
        if point.rally:
            self.rallies.append(point.rally)

        # Atualizar índices
        self._update_indices(point)

    def _update_indices(self, point: PointDetails):
        """Atualiza os índices de busca"""
        # Por set
        if point.set_number not in self._points_by_set:
            self._points_by_set[point.set_number] = []
        self._points_by_set[point.set_number].append(point)

        # Por jogador
        if point.winner_player_id not in self._points_by_player:
            self._points_by_player[point.winner_player_id] = []
        self._points_by_player[point.winner_player_id].append(point)

        # Por resultado
        if point.outcome not in self._points_by_outcome:
            self._points_by_outcome[point.outcome] = []
        self._points_by_outcome[point.outcome].append(point)

    def _rebuild_indices(self):
        """Reconstroi todos os índices"""
        self._points_by_set.clear()
        self._points_by_player.clear()
        self._points_by_outcome.clear()

        for point in self.points:
            self._update_indices(point)

    def get_points_by_set(self, set_number: int) -> List[PointDetails]:
        """
        Retorna todos os pontos de um set específico.

        Args:
            set_number: Número do set

        Returns:
            Lista de pontos do set
        """
        return self._points_by_set.get(set_number, [])

    def get_points_by_player(self, player_id: str) -> List[PointDetails]:
        """
        Retorna todos os pontos ganhos por um jogador.

        Args:
            player_id: ID do jogador

        Returns:
            Lista de pontos ganhos pelo jogador
        """
        return self._points_by_player.get(player_id, [])

    def get_points_by_outcome(self, outcome: PointOutcome) -> List[PointDetails]:
        """
        Retorna todos os pontos com um resultado específico.

        Args:
            outcome: Tipo de resultado

        Returns:
            Lista de pontos com o resultado especificado
        """
        return self._points_by_outcome.get(outcome, [])

    def get_break_points(self) -> List[PointDetails]:
        """
        Retorna todos os break points da partida.

        Returns:
            Lista de break points
        """
        return [point for point in self.points if point.is_break_point]

    def get_match_points(self) -> List[PointDetails]:
        """
        Retorna todos os match points da partida.

        Returns:
            Lista de match points
        """
        return [point for point in self.points if point.is_match_point]

    def get_longest_rallies(self, limit: int = 10) -> List[Rally]:
        """
        Retorna os rallies mais longos da partida.

        Args:
            limit: Número máximo de rallies a retornar

        Returns:
            Lista dos rallies mais longos
        """
        return sorted(self.rallies, key=lambda r: r.rally_length, reverse=True)[:limit]

    def get_fastest_serves(self, limit: int = 10) -> List[PointDetails]:
        """
        Retorna os saques mais rápidos da partida.

        Args:
            limit: Número máximo de saques a retornar

        Returns:
            Lista dos saques mais rápidos
        """
        serve_points = [p for p in self.points
                       if p.rally and p.rally.shots and
                       p.rally.shots[0].shot_type == ShotType.SERVE and
                       p.rally.shots[0].ball_speed is not None]

        return sorted(serve_points,
                     key=lambda p: p.rally.shots[0].ball_speed,
                     reverse=True)[:limit]

    def get_point_statistics(self) -> Dict:
        """
        Calcula estatísticas gerais dos pontos.

        Returns:
            Dicionário com estatísticas dos pontos
        """
        if not self.points:
            return {}

        # Estatísticas por resultado
        outcome_stats = {}
        for outcome in PointOutcome:
            count = len(self.get_points_by_outcome(outcome))
            outcome_stats[outcome.value] = count

        # Estatísticas de rally
        rally_lengths = [r.rally_length for r in self.rallies if r.rally_length > 0]
        rally_durations = [r.duration for r in self.rallies if r.duration > 0]

        # Velocidades
        all_speeds = []
        for point in self.points:
            if point.rally:
                for shot in point.rally.shots:
                    if shot.ball_speed:
                        all_speeds.append(shot.ball_speed)

        return {
            'total_points': len(self.points),
            'total_rallies': len(self.rallies),
            'outcome_distribution': outcome_stats,
            'rally_stats': {
                'avg_length': sum(rally_lengths) / len(rally_lengths) if rally_lengths else 0,
                'max_length': max(rally_lengths) if rally_lengths else 0,
                'avg_duration': sum(rally_durations) / len(rally_durations) if rally_durations else 0,
                'max_duration': max(rally_durations) if rally_durations else 0
            },
            'speed_stats': {
                'avg_speed': sum(all_speeds) / len(all_speeds) if all_speeds else 0,
                'max_speed': max(all_speeds) if all_speeds else 0,
                'min_speed': min(all_speeds) if all_speeds else 0
            },
            'break_points': len(self.get_break_points()),
            'match_points': len(self.get_match_points())
        }

    def export_for_analysis(self) -> Dict:
        """
        Exporta dados para análise externa.

        Returns:
            Dicionário com todos os dados estruturados
        """
        return {
            'match_id': self.match_id,
            'points': [
                {
                    'point_id': p.point_id,
                    'timestamp': p.timestamp.isoformat(),
                    'set_number': p.set_number,
                    'game_number': p.game_number,
                    'point_number': p.point_number,
                    'serving_player_id': p.serving_player_id,
                    'winner_player_id': p.winner_player_id,
                    'outcome': p.outcome.value,
                    'duration': p.duration,
                    'is_break_point': p.is_break_point,
                    'is_match_point': p.is_match_point,
                    'rally_length': p.rally.rally_length if p.rally else 0,
                    'max_speed': p.max_rally_speed
                }
                for p in self.points
            ],
            'statistics': self.get_point_statistics()
        }

    def to_dict(self) -> Dict:
        """
        Converte o histórico para dicionário.

        Returns:
            Dicionário completo do histórico
        """
        return {
            'match_id': self.match_id,
            'total_points': len(self.points),
            'total_rallies': len(self.rallies),
            'statistics': self.get_point_statistics(),
            'last_update': datetime.now().isoformat()
        }

    def __len__(self) -> int:
        return len(self.points)

    def __str__(self) -> str:
        return f"PointHistory({self.match_id}: {len(self.points)} points)"

    def __repr__(self) -> str:
        return self.__str__()