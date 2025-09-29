"""
Match Model - Modelo de Partida

Define a estrutura de dados para representar uma partida completa de tênis,
incluindo jogadores, pontuação, sets, games e histórico de eventos.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from .player import Player
from .court import Court


class MatchType(Enum):
    """Tipos de partida"""
    SINGLES = "singles"
    DOUBLES = "doubles"


class MatchFormat(Enum):
    """Formatos de partida"""
    BEST_OF_3 = "best_of_3"  # Melhor de 3 sets
    BEST_OF_5 = "best_of_5"  # Melhor de 5 sets


class MatchStatus(Enum):
    """Status da partida"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class TiebreakType(Enum):
    """Tipos de tiebreak"""
    STANDARD = "standard"  # Primeiro a 7 pontos
    SUPER = "super"        # Primeiro a 10 pontos
    FINAL_SET = "final_set"  # Tiebreak do set final


@dataclass
class GameScore:
    """Pontuação de um game"""
    player1_points: int = 0  # 0, 15, 30, 40, AD
    player2_points: int = 0
    is_deuce: bool = False
    has_advantage: Optional[str] = None  # player_id com vantagem
    is_completed: bool = False
    winner: Optional[str] = None  # player_id do vencedor


@dataclass
class SetScore:
    """Pontuação de um set"""
    player1_games: int = 0
    player2_games: int = 0
    player1_tiebreak: int = 0
    player2_tiebreak: int = 0
    is_tiebreak: bool = False
    is_completed: bool = False
    winner: Optional[str] = None  # player_id do vencedor


@dataclass
class MatchEvent:
    """Evento durante a partida"""
    event_id: str
    timestamp: datetime
    event_type: str  # ace, winner, error, break_point, etc.
    player_id: str
    description: str
    set_number: int
    game_number: int
    point_number: int
    score_before: Dict
    score_after: Dict
    additional_data: Dict = field(default_factory=dict)


@dataclass
class Match:
    """
    Modelo completo de uma partida de tênis.

    Contém todas as informações sobre uma partida, incluindo jogadores,
    pontuação atual, histórico completo e configurações da partida.
    """

    # Identificação da partida
    match_id: str
    tournament_name: str = ""
    round_name: str = ""  # "R1", "QF", "SF", "F", etc.

    # Configurações da partida
    match_type: MatchType = MatchType.SINGLES
    match_format: MatchFormat = MatchFormat.BEST_OF_3
    tiebreak_type: TiebreakType = TiebreakType.STANDARD

    # Jogadores
    player1: Player
    player2: Player

    # Quadra
    court: Court

    # Estado da partida
    status: MatchStatus = MatchStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Pontuação atual
    current_set: int = 1
    current_game: int = 1
    current_point: int = 1
    serving_player: Optional[str] = None  # player_id

    # Sets
    sets: List[SetScore] = field(default_factory=list)
    current_set_score: SetScore = field(default_factory=SetScore)

    # Game atual
    current_game_score: GameScore = field(default_factory=GameScore)

    # Histórico de eventos
    events: List[MatchEvent] = field(default_factory=list)

    # Estatísticas da partida
    match_stats: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Inicialização após criação"""
        if not self.sets:
            self.sets.append(SetScore())
            self.current_set_score = self.sets[0]

    def start_match(self, serving_player_id: str):
        """
        Inicia a partida.

        Args:
            serving_player_id: ID do jogador que vai sacar primeiro
        """
        self.status = MatchStatus.IN_PROGRESS
        self.start_time = datetime.now()
        self.serving_player = serving_player_id

        # Definir jogador que saca
        if serving_player_id == self.player1.player_id:
            self.player1.is_serving = True
            self.player2.is_serving = False
        else:
            self.player1.is_serving = False
            self.player2.is_serving = True

        # Registrar evento de início
        self._add_event("match_start", serving_player_id, "Início da partida")

    def add_point(self, winner_player_id: str, point_type: str = "normal", **kwargs):
        """
        Adiciona um ponto para um jogador.

        Args:
            winner_player_id: ID do jogador que ganhou o ponto
            point_type: Tipo do ponto (ace, winner, error, etc.)
            **kwargs: Dados adicionais do ponto
        """
        # Salvar estado anterior
        score_before = self._get_current_score()

        # Atualizar pontuação do game
        if winner_player_id == self.player1.player_id:
            self._add_point_to_game("player1")
        else:
            self._add_point_to_game("player2")

        # Verificar se o game terminou
        if self.current_game_score.is_completed:
            self._complete_game(self.current_game_score.winner)

        # Atualizar estatísticas do jogador
        self._update_player_stats(winner_player_id, point_type, **kwargs)

        # Registrar evento
        score_after = self._get_current_score()
        self._add_event(
            point_type,
            winner_player_id,
            f"Ponto para {self._get_player_name(winner_player_id)}",
            score_before=score_before,
            score_after=score_after,
            additional_data=kwargs
        )

        self.current_point += 1

    def _add_point_to_game(self, player: str):
        """Adiciona um ponto no game atual"""
        if player == "player1":
            if self.current_game_score.player1_points == 0:
                self.current_game_score.player1_points = 15
            elif self.current_game_score.player1_points == 15:
                self.current_game_score.player1_points = 30
            elif self.current_game_score.player1_points == 30:
                self.current_game_score.player1_points = 40
            elif self.current_game_score.player1_points == 40:
                # Verificar se ganha o game ou vai para deuce/vantagem
                if self.current_game_score.player2_points < 40:
                    # Ganha o game
                    self.current_game_score.is_completed = True
                    self.current_game_score.winner = self.player1.player_id
                elif self.current_game_score.player2_points == 40:
                    # Vantagem
                    if not self.current_game_score.is_deuce:
                        self.current_game_score.is_deuce = True
                    self.current_game_score.has_advantage = self.player1.player_id
                elif self.current_game_score.has_advantage == self.player2.player_id:
                    # Remove vantagem do adversário, volta para deuce
                    self.current_game_score.has_advantage = None
                elif self.current_game_score.has_advantage == self.player1.player_id:
                    # Já tem vantagem, ganha o game
                    self.current_game_score.is_completed = True
                    self.current_game_score.winner = self.player1.player_id

        else:  # player2
            if self.current_game_score.player2_points == 0:
                self.current_game_score.player2_points = 15
            elif self.current_game_score.player2_points == 15:
                self.current_game_score.player2_points = 30
            elif self.current_game_score.player2_points == 30:
                self.current_game_score.player2_points = 40
            elif self.current_game_score.player2_points == 40:
                # Verificar se ganha o game ou vai para deuce/vantagem
                if self.current_game_score.player1_points < 40:
                    # Ganha o game
                    self.current_game_score.is_completed = True
                    self.current_game_score.winner = self.player2.player_id
                elif self.current_game_score.player1_points == 40:
                    # Vantagem
                    if not self.current_game_score.is_deuce:
                        self.current_game_score.is_deuce = True
                    self.current_game_score.has_advantage = self.player2.player_id
                elif self.current_game_score.has_advantage == self.player1.player_id:
                    # Remove vantagem do adversário, volta para deuce
                    self.current_game_score.has_advantage = None
                elif self.current_game_score.has_advantage == self.player2.player_id:
                    # Já tem vantagem, ganha o game
                    self.current_game_score.is_completed = True
                    self.current_game_score.winner = self.player2.player_id

    def _complete_game(self, winner_player_id: str):
        """Completa um game e atualiza o set"""
        # Adicionar game ao vencedor
        if winner_player_id == self.player1.player_id:
            self.current_set_score.player1_games += 1
        else:
            self.current_set_score.player2_games += 1

        # Verificar se o set terminou
        if self._is_set_completed():
            self._complete_set(self._get_set_winner())

        # Trocar sacador
        self._switch_server()

        # Resetar game score
        self.current_game_score = GameScore()
        self.current_game += 1

    def _is_set_completed(self) -> bool:
        """Verifica se o set atual está completo"""
        p1_games = self.current_set_score.player1_games
        p2_games = self.current_set_score.player2_games

        # Set normal (primeiro a 6 com diferença de 2)
        if p1_games >= 6 and p1_games - p2_games >= 2:
            return True
        if p2_games >= 6 and p2_games - p1_games >= 2:
            return True

        # Tiebreak (6-6)
        if p1_games == 6 and p2_games == 6:
            # Iniciar tiebreak se ainda não começou
            if not self.current_set_score.is_tiebreak:
                self.current_set_score.is_tiebreak = True
                return False

            # Verificar se tiebreak terminou
            tb1 = self.current_set_score.player1_tiebreak
            tb2 = self.current_set_score.player2_tiebreak

            if self.tiebreak_type == TiebreakType.STANDARD:
                return (tb1 >= 7 and tb1 - tb2 >= 2) or (tb2 >= 7 and tb2 - tb1 >= 2)
            elif self.tiebreak_type == TiebreakType.SUPER:
                return (tb1 >= 10 and tb1 - tb2 >= 2) or (tb2 >= 10 and tb2 - tb1 >= 2)

        return False

    def _get_set_winner(self) -> str:
        """Retorna o vencedor do set atual"""
        p1_games = self.current_set_score.player1_games
        p2_games = self.current_set_score.player2_games
        p1_tb = self.current_set_score.player1_tiebreak
        p2_tb = self.current_set_score.player2_tiebreak

        if self.current_set_score.is_tiebreak:
            return self.player1.player_id if p1_tb > p2_tb else self.player2.player_id
        else:
            return self.player1.player_id if p1_games > p2_games else self.player2.player_id

    def _complete_set(self, winner_player_id: str):
        """Completa um set"""
        self.current_set_score.is_completed = True
        self.current_set_score.winner = winner_player_id

        # Verificar se a partida terminou
        if self._is_match_completed():
            self._complete_match(self._get_match_winner())
        else:
            # Iniciar novo set
            self.current_set += 1
            self.current_game = 1
            new_set = SetScore()
            self.sets.append(new_set)
            self.current_set_score = new_set

    def _is_match_completed(self) -> bool:
        """Verifica se a partida está completa"""
        sets_won_p1 = sum(1 for s in self.sets if s.winner == self.player1.player_id)
        sets_won_p2 = sum(1 for s in self.sets if s.winner == self.player2.player_id)

        if self.match_format == MatchFormat.BEST_OF_3:
            return sets_won_p1 >= 2 or sets_won_p2 >= 2
        else:  # BEST_OF_5
            return sets_won_p1 >= 3 or sets_won_p2 >= 3

    def _get_match_winner(self) -> str:
        """Retorna o vencedor da partida"""
        sets_won_p1 = sum(1 for s in self.sets if s.winner == self.player1.player_id)
        sets_won_p2 = sum(1 for s in self.sets if s.winner == self.player2.player_id)

        return self.player1.player_id if sets_won_p1 > sets_won_p2 else self.player2.player_id

    def _complete_match(self, winner_player_id: str):
        """Completa a partida"""
        self.status = MatchStatus.COMPLETED
        self.end_time = datetime.now()
        self._add_event("match_end", winner_player_id, f"Vitória de {self._get_player_name(winner_player_id)}")

    def _switch_server(self):
        """Troca o sacador"""
        if self.serving_player == self.player1.player_id:
            self.serving_player = self.player2.player_id
            self.player1.is_serving = False
            self.player2.is_serving = True
        else:
            self.serving_player = self.player1.player_id
            self.player1.is_serving = True
            self.player2.is_serving = False

    def _update_player_stats(self, player_id: str, point_type: str, **kwargs):
        """Atualiza estatísticas do jogador"""
        player = self.player1 if player_id == self.player1.player_id else self.player2
        player.update_stats(point_type, **kwargs)
        player.stats.total_points_won += 1

    def _add_event(self, event_type: str, player_id: str, description: str, **kwargs):
        """Adiciona um evento ao histórico"""
        event = MatchEvent(
            event_id=f"{self.match_id}_{len(self.events)+1}",
            timestamp=datetime.now(),
            event_type=event_type,
            player_id=player_id,
            description=description,
            set_number=self.current_set,
            game_number=self.current_game,
            point_number=self.current_point,
            score_before=kwargs.get('score_before', {}),
            score_after=kwargs.get('score_after', {}),
            additional_data=kwargs.get('additional_data', {})
        )
        self.events.append(event)

    def _get_current_score(self) -> Dict:
        """Retorna a pontuação atual"""
        return {
            'set': self.current_set,
            'game': self.current_game,
            'point': self.current_point,
            'sets': [{'p1': s.player1_games, 'p2': s.player2_games} for s in self.sets],
            'current_game': {
                'p1': self.current_game_score.player1_points,
                'p2': self.current_game_score.player2_points,
                'deuce': self.current_game_score.is_deuce,
                'advantage': self.current_game_score.has_advantage
            },
            'serving': self.serving_player
        }

    def _get_player_name(self, player_id: str) -> str:
        """Retorna o nome do jogador pelo ID"""
        if player_id == self.player1.player_id:
            return self.player1.info.name
        else:
            return self.player2.info.name

    def get_score_string(self) -> str:
        """
        Retorna a pontuação atual como string.

        Returns:
            String formatada com a pontuação atual
        """
        # Pontuação dos sets
        sets_score = []
        for i, set_score in enumerate(self.sets):
            if i < self.current_set - 1:  # Sets já completados
                p1_score = set_score.player1_games
                p2_score = set_score.player2_games
                if set_score.is_tiebreak and set_score.is_completed:
                    tb_winner = "1" if set_score.winner == self.player1.player_id else "2"
                    tb_loser = "2" if tb_winner == "1" else "1"
                    tb_winner_score = set_score.player1_tiebreak if tb_winner == "1" else set_score.player2_tiebreak
                    sets_score.append(f"{p1_score}-{p2_score}({tb_winner_score})")
                else:
                    sets_score.append(f"{p1_score}-{p2_score}")

        # Set atual
        current_p1 = self.current_set_score.player1_games
        current_p2 = self.current_set_score.player2_games
        sets_score.append(f"{current_p1}-{current_p2}")

        sets_str = " ".join(sets_score)

        # Game atual
        if self.current_set_score.is_tiebreak:
            tb1 = self.current_set_score.player1_tiebreak
            tb2 = self.current_set_score.player2_tiebreak
            game_str = f"TB: {tb1}-{tb2}"
        else:
            p1_points = self.current_game_score.player1_points
            p2_points = self.current_game_score.player2_points

            # Converter pontos para formato de tênis
            point_map = {0: "0", 15: "15", 30: "30", 40: "40"}

            if self.current_game_score.is_deuce:
                if self.current_game_score.has_advantage == self.player1.player_id:
                    game_str = "AD-40"
                elif self.current_game_score.has_advantage == self.player2.player_id:
                    game_str = "40-AD"
                else:
                    game_str = "40-40"
            else:
                p1_str = point_map.get(p1_points, str(p1_points))
                p2_str = point_map.get(p2_points, str(p2_points))
                game_str = f"{p1_str}-{p2_str}"

        return f"{self.player1.info.name} vs {self.player2.info.name} | {sets_str} | {game_str}"

    def to_dict(self) -> Dict:
        """
        Converte a partida para um dicionário.

        Returns:
            Dicionário com todos os dados da partida
        """
        return {
            'match_id': self.match_id,
            'tournament_name': self.tournament_name,
            'round_name': self.round_name,
            'match_type': self.match_type.value,
            'match_format': self.match_format.value,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'players': {
                'player1': self.player1.to_dict(),
                'player2': self.player2.to_dict()
            },
            'score': self._get_current_score(),
            'score_string': self.get_score_string(),
            'events_count': len(self.events)
        }

    def __str__(self) -> str:
        return f"Match({self.match_id}: {self.get_score_string()})"

    def __repr__(self) -> str:
        return self.__str__()