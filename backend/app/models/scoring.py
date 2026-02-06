"""
Scoring models for tennis match scoring system
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class MatchFormat(str, Enum):
    """Match format enumeration"""
    BEST_OF_3 = "best_of_3"
    BEST_OF_5 = "best_of_5"


class ScoreValue(str, Enum):
    """Tennis score values"""
    LOVE = "0"
    FIFTEEN = "15"
    THIRTY = "30"
    FORTY = "40"
    ADVANTAGE = "AD"
    GAME = "GAME"


class GameScore(BaseModel):
    """Game score for a single game"""
    player1_points: int = Field(default=0, ge=0, description="Points for player 1 (0-4+)")
    player2_points: int = Field(default=0, ge=0, description="Points for player 2 (0-4+)")
    server_player_id: str = Field(..., description="ID of the serving player")
    is_tiebreak: bool = Field(default=False, description="Whether this is a tiebreak game")
    is_complete: bool = Field(default=False, description="Whether the game is complete")
    winner_player_id: Optional[str] = Field(default=None, description="Winner player ID if complete")

    def get_score_display(self) -> tuple[str, str]:
        """
        Get display score for the game
        Returns tuple (player1_score, player2_score)
        """
        if self.is_tiebreak:
            return str(self.player1_points), str(self.player2_points)

        # Regular game scoring
        score_map = {0: "0", 1: "15", 2: "30", 3: "40"}

        # Handle deuce and advantage
        if self.player1_points >= 3 and self.player2_points >= 3:
            diff = self.player1_points - self.player2_points
            if diff == 0:
                return "40", "40"  # Deuce
            elif diff > 0:
                return "AD", "40"  # Advantage player 1
            else:
                return "40", "AD"  # Advantage player 2

        # Normal scoring
        p1_score = score_map.get(self.player1_points, "40")
        p2_score = score_map.get(self.player2_points, "40")

        return p1_score, p2_score

    def add_point(self, player_id: str) -> bool:
        """
        Add a point to the specified player
        Returns True if game is won
        """
        if self.is_complete:
            return False

        if player_id == self.server_player_id:
            is_player1 = True  # Assuming server is player1 for now
        else:
            is_player1 = False

        if is_player1:
            self.player1_points += 1
        else:
            self.player2_points += 1

        # Check if game is won
        if self.is_tiebreak:
            # Tiebreak: first to 7, win by 2
            max_points = max(self.player1_points, self.player2_points)
            point_diff = abs(self.player1_points - self.player2_points)
            if max_points >= 7 and point_diff >= 2:
                self.is_complete = True
                self.winner_player_id = player_id
                return True
        else:
            # Regular game: first to 4 points, win by 2
            max_points = max(self.player1_points, self.player2_points)
            point_diff = abs(self.player1_points - self.player2_points)
            if max_points >= 4 and point_diff >= 2:
                self.is_complete = True
                self.winner_player_id = player_id
                return True

        return False


class SetScore(BaseModel):
    """Set score for a single set"""
    player1_games: int = Field(default=0, ge=0, description="Games won by player 1")
    player2_games: int = Field(default=0, ge=0, description="Games won by player 2")
    tiebreak_score: Optional[tuple[int, int]] = Field(default=None, description="Tiebreak score if applicable")
    is_complete: bool = Field(default=False, description="Whether the set is complete")
    winner_player_id: Optional[str] = Field(default=None, description="Winner player ID if complete")

    def add_game(self, player_id: str, is_tiebreak: bool = False, tiebreak_score: Optional[tuple[int, int]] = None) -> bool:
        """
        Add a game to the specified player
        Returns True if set is won
        """
        if self.is_complete:
            return False

        # Assuming player_id comparison logic here (simplified)
        # In production, you'd need proper player1/player2 mapping
        is_player1 = True  # Placeholder

        if is_player1:
            self.player1_games += 1
        else:
            self.player2_games += 1

        if is_tiebreak:
            self.tiebreak_score = tiebreak_score

        # Check if set is won
        max_games = max(self.player1_games, self.player2_games)
        game_diff = abs(self.player1_games - self.player2_games)

        # Set won by reaching 6 games with 2-game lead, or winning tiebreak at 6-6
        if (max_games >= 6 and game_diff >= 2) or (self.player1_games == 7 or self.player2_games == 7):
            self.is_complete = True
            self.winner_player_id = player_id
            return True

        return False


class MatchScore(BaseModel):
    """Complete match score"""
    match_id: str = Field(..., description="Match ID")
    player1_id: str = Field(..., description="Player 1 ID")
    player2_id: str = Field(..., description="Player 2 ID")
    format: MatchFormat = Field(default=MatchFormat.BEST_OF_3, description="Match format")

    sets: List[SetScore] = Field(default_factory=list, description="Set scores")
    current_set: Optional[SetScore] = Field(default=None, description="Current set in progress")
    current_game: Optional[GameScore] = Field(default=None, description="Current game in progress")

    current_server_id: str = Field(..., description="Current server player ID")
    is_complete: bool = Field(default=False, description="Whether the match is complete")
    winner_player_id: Optional[str] = Field(default=None, description="Winner player ID if complete")

    def get_sets_won(self, player_id: str) -> int:
        """Get number of sets won by player"""
        return sum(1 for s in self.sets if s.winner_player_id == player_id)

    def is_tiebreak_needed(self) -> bool:
        """Check if current game should be a tiebreak"""
        if not self.current_set:
            return False
        return self.current_set.player1_games == 6 and self.current_set.player2_games == 6

    def switch_server(self):
        """Switch the server for the next game"""
        self.current_server_id = self.player2_id if self.current_server_id == self.player1_id else self.player1_id

    def start_new_game(self):
        """Start a new game"""
        is_tiebreak = self.is_tiebreak_needed()
        self.current_game = GameScore(
            server_player_id=self.current_server_id,
            is_tiebreak=is_tiebreak
        )

    def start_new_set(self):
        """Start a new set"""
        self.current_set = SetScore()

    def add_point(self, winner_player_id: str) -> dict:
        """
        Add a point to the match
        Returns dict with events that occurred (game_won, set_won, match_won)
        """
        events = {
            "point_won": True,
            "game_won": False,
            "set_won": False,
            "match_won": False
        }

        if self.is_complete:
            return events

        # Initialize if needed
        if not self.current_set:
            self.start_new_set()
        if not self.current_game:
            self.start_new_game()

        # Add point to current game
        game_won = self.current_game.add_point(winner_player_id)

        if game_won:
            events["game_won"] = True

            # Add game to set
            tiebreak_score = None
            if self.current_game.is_tiebreak:
                tiebreak_score = (self.current_game.player1_points, self.current_game.player2_points)

            set_won = self.current_set.add_game(
                winner_player_id,
                is_tiebreak=self.current_game.is_tiebreak,
                tiebreak_score=tiebreak_score
            )

            if set_won:
                events["set_won"] = True
                self.sets.append(self.current_set)

                # Check if match is won
                sets_won = self.get_sets_won(winner_player_id)
                sets_needed = 3 if self.format == MatchFormat.BEST_OF_5 else 2

                if sets_won >= sets_needed:
                    events["match_won"] = True
                    self.is_complete = True
                    self.winner_player_id = winner_player_id
                    self.current_set = None
                    self.current_game = None
                else:
                    # Start new set
                    self.start_new_set()
                    self.switch_server()
                    self.start_new_game()
            else:
                # Start new game in same set
                self.switch_server()
                self.start_new_game()

        return events


class GameSituation(BaseModel):
    """Game situation indicators"""
    is_break_point: bool = Field(default=False, description="Server is one point away from losing game")
    is_set_point: bool = Field(default=False, description="Player is one point away from winning set")
    is_match_point: bool = Field(default=False, description="Player is one point away from winning match")
    is_deuce: bool = Field(default=False, description="Game is at deuce (40-40)")
    is_advantage: bool = Field(default=False, description="One player has advantage")
    advantage_player_id: Optional[str] = Field(default=None, description="Player ID with advantage")
    is_tiebreak: bool = Field(default=False, description="Currently in tiebreak")
    is_bagel_possible: bool = Field(default=False, description="Possible 6-0 set (bagel)")
    is_breadstick_possible: bool = Field(default=False, description="Possible 6-1 set (breadstick)")
    break_point_player_id: Optional[str] = Field(default=None, description="Player ID with break point opportunity")
    set_point_player_id: Optional[str] = Field(default=None, description="Player ID with set point opportunity")
    match_point_player_id: Optional[str] = Field(default=None, description="Player ID with match point opportunity")
    situation_text: str = Field(default="", description="Human-readable situation description")


class ScoreUpdate(BaseModel):
    """Score update event"""
    match_id: str
    point_winner_id: str
    timestamp: str
    events: dict = Field(default_factory=dict, description="Events that occurred (game_won, set_won, etc)")
    situation: Optional[GameSituation] = Field(default=None, description="Current game situation")
