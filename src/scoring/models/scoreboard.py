"""
Scoreboard Model - Modelo de Placar

Define a estrutura do placar em tempo real para visualização
e transmissão de dados de pontuação.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class ScoreboardStyle(Enum):
    """Estilos de visualização do placar"""
    TRADITIONAL = "traditional"  # Estilo clássico
    MODERN = "modern"           # Estilo moderno
    BROADCAST = "broadcast"     # Para transmissão
    MOBILE = "mobile"          # Para dispositivos móveis


@dataclass
class PlayerScoreDisplay:
    """Informações de display para um jogador"""
    name: str
    short_name: str  # Nome abreviado (ex: "R. FEDERER")
    country_code: str = ""  # Código do país (ex: "SUI")
    ranking: Optional[int] = None
    seed: Optional[int] = None  # Cabeça de chave

    # Cores personalizadas
    primary_color: str = "#FFFFFF"
    secondary_color: str = "#000000"


@dataclass
class GameScoreDisplay:
    """Pontuação visual de um game"""
    points: str  # "0", "15", "30", "40", "AD"
    is_serving: bool = False
    is_advantage: bool = False
    is_winner: bool = False


@dataclass
class SetScoreDisplay:
    """Pontuação visual de um set"""
    games: int
    tiebreak_points: int = 0
    is_current: bool = False
    is_completed: bool = False
    is_winner: bool = False


@dataclass
class MatchStatsDisplay:
    """Estatísticas para exibição"""
    aces: int = 0
    double_faults: int = 0
    first_serve_percentage: int = 0
    winners: int = 0
    unforced_errors: int = 0
    break_points_converted: str = "0/0"  # "2/5"

    # Estatísticas avançadas
    total_points_won: int = 0
    max_speed: Optional[float] = None
    avg_speed: Optional[float] = None


@dataclass
class Scoreboard:
    """
    Modelo completo do placar para visualização.

    Contém todas as informações formatadas para exibição
    em diferentes tipos de interface (TV, mobile, web, etc.).
    """

    # Identificação
    match_id: str
    style: ScoreboardStyle = ScoreboardStyle.TRADITIONAL
    last_update: datetime = field(default_factory=datetime.now)

    # Informações da partida
    tournament_name: str = ""
    round_name: str = ""
    court_name: str = ""
    match_format: str = "Best of 3"  # "Best of 3", "Best of 5"
    surface: str = ""  # "Hard", "Clay", "Grass"

    # Tempo
    match_duration: str = "0:00"
    current_time: str = ""

    # Jogadores
    player1: PlayerScoreDisplay
    player2: PlayerScoreDisplay

    # Pontuação atual
    player1_sets: List[SetScoreDisplay] = field(default_factory=list)
    player2_sets: List[SetScoreDisplay] = field(default_factory=list)

    player1_current_game: GameScoreDisplay = field(default_factory=lambda: GameScoreDisplay("0"))
    player2_current_game: GameScoreDisplay = field(default_factory=lambda: GameScoreDisplay("0"))

    # Estado especial
    is_tiebreak: bool = False
    is_deuce: bool = False
    is_break_point: bool = False
    is_match_point: bool = False
    is_set_point: bool = False

    # Estatísticas
    player1_stats: MatchStatsDisplay = field(default_factory=MatchStatsDisplay)
    player2_stats: MatchStatsDisplay = field(default_factory=MatchStatsDisplay)

    # Configurações de exibição
    show_stats: bool = True
    show_speed: bool = True
    show_serve_clock: bool = False
    serve_clock_seconds: int = 0

    # Mensagens e alertas
    status_message: str = ""  # "In Progress", "Rain Delay", etc.
    special_message: str = ""  # "Break Point", "Match Point", etc.

    def update_from_match(self, match):
        """
        Atualiza o placar baseado no estado atual da partida.

        Args:
            match: Objeto Match com dados atualizados
        """
        self.last_update = datetime.now()

        # Atualizar informações básicas
        self.tournament_name = match.tournament_name
        self.round_name = match.round_name
        self.match_format = f"Best of {3 if match.match_format.value == 'best_of_3' else 5}"

        # Atualizar jogadores
        self.player1.name = match.player1.info.name
        self.player1.ranking = match.player1.info.ranking

        self.player2.name = match.player2.info.name
        self.player2.ranking = match.player2.info.ranking

        # Atualizar pontuação dos sets
        self._update_sets_display(match)

        # Atualizar game atual
        self._update_current_game(match)

        # Atualizar estatísticas
        self._update_statistics(match)

        # Atualizar status especiais
        self._update_special_status(match)

        # Calcular duração
        if match.start_time:
            duration = datetime.now() - match.start_time
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            self.match_duration = f"{hours}:{minutes:02d}" if hours > 0 else f"{minutes}:00"

    def _update_sets_display(self, match):
        """Atualiza a exibição dos sets"""
        self.player1_sets = []
        self.player2_sets = []

        for i, set_score in enumerate(match.sets):
            # Set do Player 1
            p1_set = SetScoreDisplay(
                games=set_score.player1_games,
                tiebreak_points=set_score.player1_tiebreak if set_score.is_tiebreak else 0,
                is_current=(i == match.current_set - 1),
                is_completed=set_score.is_completed,
                is_winner=(set_score.winner == match.player1.player_id)
            )
            self.player1_sets.append(p1_set)

            # Set do Player 2
            p2_set = SetScoreDisplay(
                games=set_score.player2_games,
                tiebreak_points=set_score.player2_tiebreak if set_score.is_tiebreak else 0,
                is_current=(i == match.current_set - 1),
                is_completed=set_score.is_completed,
                is_winner=(set_score.winner == match.player2.player_id)
            )
            self.player2_sets.append(p2_set)

    def _update_current_game(self, match):
        """Atualiza a exibição do game atual"""
        game = match.current_game_score

        # Converter pontos para formato de display
        def points_to_display(points, has_advantage, is_opponent_advantage):
            if points == 0:
                return "0"
            elif points == 15:
                return "15"
            elif points == 30:
                return "30"
            elif points == 40:
                if has_advantage:
                    return "AD"
                elif is_opponent_advantage:
                    return "40"
                else:
                    return "40"
            return str(points)

        # Player 1
        p1_has_advantage = (game.has_advantage == match.player1.player_id)
        p2_has_advantage = (game.has_advantage == match.player2.player_id)

        if match.current_set_score.is_tiebreak:
            # Tiebreak: mostrar pontos diretos
            self.player1_current_game = GameScoreDisplay(
                points=str(match.current_set_score.player1_tiebreak),
                is_serving=(match.serving_player == match.player1.player_id),
                is_advantage=False
            )
            self.player2_current_game = GameScoreDisplay(
                points=str(match.current_set_score.player2_tiebreak),
                is_serving=(match.serving_player == match.player2.player_id),
                is_advantage=False
            )
            self.is_tiebreak = True
        else:
            # Game normal
            self.player1_current_game = GameScoreDisplay(
                points=points_to_display(game.player1_points, p1_has_advantage, p2_has_advantage),
                is_serving=(match.serving_player == match.player1.player_id),
                is_advantage=p1_has_advantage
            )
            self.player2_current_game = GameScoreDisplay(
                points=points_to_display(game.player2_points, p2_has_advantage, p1_has_advantage),
                is_serving=(match.serving_player == match.player2.player_id),
                is_advantage=p2_has_advantage
            )
            self.is_tiebreak = False

        self.is_deuce = game.is_deuce

    def _update_statistics(self, match):
        """Atualiza as estatísticas para exibição"""
        # Player 1
        p1_stats = match.player1.stats
        self.player1_stats = MatchStatsDisplay(
            aces=p1_stats.aces,
            double_faults=p1_stats.double_faults,
            first_serve_percentage=int(p1_stats.first_serve_percentage),
            winners=p1_stats.winners,
            unforced_errors=p1_stats.unforced_errors,
            total_points_won=p1_stats.total_points_won,
            max_speed=p1_stats.max_speed
        )

        # Player 2
        p2_stats = match.player2.stats
        self.player2_stats = MatchStatsDisplay(
            aces=p2_stats.aces,
            double_faults=p2_stats.double_faults,
            first_serve_percentage=int(p2_stats.first_serve_percentage),
            winners=p2_stats.winners,
            unforced_errors=p2_stats.unforced_errors,
            total_points_won=p2_stats.total_points_won,
            max_speed=p2_stats.max_speed
        )

    def _update_special_status(self, match):
        """Atualiza status especiais (break point, match point, etc.)"""
        # Implementar lógica para detectar situações especiais
        # Por enquanto, placeholders simples
        self.is_break_point = False  # TODO: implementar detecção
        self.is_match_point = False  # TODO: implementar detecção
        self.is_set_point = False   # TODO: implementar detecção

        # Atualizar mensagens
        if match.status.value == "in_progress":
            self.status_message = "Live"
        elif match.status.value == "completed":
            self.status_message = "Final"
        else:
            self.status_message = match.status.value.title()

        # Mensagem especial baseada em situações
        if self.is_match_point:
            self.special_message = "Match Point"
        elif self.is_set_point:
            self.special_message = "Set Point"
        elif self.is_break_point:
            self.special_message = "Break Point"
        elif self.is_deuce:
            self.special_message = "Deuce"
        else:
            self.special_message = ""

    def get_score_for_broadcast(self) -> Dict:
        """
        Retorna dados formatados para transmissão.

        Returns:
            Dicionário com dados prontos para broadcast
        """
        return {
            'match_info': {
                'tournament': self.tournament_name,
                'round': self.round_name,
                'court': self.court_name,
                'format': self.match_format,
                'surface': self.surface,
                'duration': self.match_duration,
                'status': self.status_message
            },
            'players': {
                'player1': {
                    'name': self.player1.name,
                    'short_name': self.player1.short_name,
                    'country': self.player1.country_code,
                    'ranking': self.player1.ranking,
                    'seed': self.player1.seed
                },
                'player2': {
                    'name': self.player2.name,
                    'short_name': self.player2.short_name,
                    'country': self.player2.country_code,
                    'ranking': self.player2.ranking,
                    'seed': self.player2.seed
                }
            },
            'score': {
                'sets': {
                    'player1': [{'games': s.games, 'tb': s.tiebreak_points} for s in self.player1_sets],
                    'player2': [{'games': s.games, 'tb': s.tiebreak_points} for s in self.player2_sets]
                },
                'current_game': {
                    'player1': {
                        'points': self.player1_current_game.points,
                        'serving': self.player1_current_game.is_serving,
                        'advantage': self.player1_current_game.is_advantage
                    },
                    'player2': {
                        'points': self.player2_current_game.points,
                        'serving': self.player2_current_game.is_serving,
                        'advantage': self.player2_current_game.is_advantage
                    }
                },
                'special': {
                    'is_tiebreak': self.is_tiebreak,
                    'is_deuce': self.is_deuce,
                    'is_break_point': self.is_break_point,
                    'is_match_point': self.is_match_point,
                    'special_message': self.special_message
                }
            },
            'statistics': {
                'player1': self.player1_stats.__dict__,
                'player2': self.player2_stats.__dict__
            }
        }

    def to_dict(self) -> Dict:
        """
        Converte o placar para dicionário.

        Returns:
            Dicionário completo do placar
        """
        return {
            'match_id': self.match_id,
            'style': self.style.value,
            'last_update': self.last_update.isoformat(),
            'tournament_name': self.tournament_name,
            'round_name': self.round_name,
            'court_name': self.court_name,
            'match_format': self.match_format,
            'match_duration': self.match_duration,
            'players': {
                'player1': self.player1.__dict__,
                'player2': self.player2.__dict__
            },
            'sets': {
                'player1': [s.__dict__ for s in self.player1_sets],
                'player2': [s.__dict__ for s in self.player2_sets]
            },
            'current_game': {
                'player1': self.player1_current_game.__dict__,
                'player2': self.player2_current_game.__dict__
            },
            'status': {
                'is_tiebreak': self.is_tiebreak,
                'is_deuce': self.is_deuce,
                'is_break_point': self.is_break_point,
                'is_match_point': self.is_match_point,
                'status_message': self.status_message,
                'special_message': self.special_message
            },
            'statistics': {
                'player1': self.player1_stats.__dict__,
                'player2': self.player2_stats.__dict__
            }
        }

    def __str__(self) -> str:
        sets_p1 = " ".join([f"{s.games}" for s in self.player1_sets])
        sets_p2 = " ".join([f"{s.games}" for s in self.player2_sets])

        return (f"Scoreboard({self.player1.short_name} {sets_p1} [{self.player1_current_game.points}] "
                f"vs {self.player2.short_name} {sets_p2} [{self.player2_current_game.points}])")

    def __repr__(self) -> str:
        return self.__str__()