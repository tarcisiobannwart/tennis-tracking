"""
Scoreboard models for visual score display
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class ScoreboardStyle(str, Enum):
    """Scoreboard display styles"""
    TRADITIONAL = "traditional"  # Classic ATP/WTA style
    MODERN = "modern"  # Modern minimal design
    TV_BROADCAST = "tv_broadcast"  # TV broadcast style with player photos
    MOBILE = "mobile"  # Optimized for mobile screens
    COMPACT = "compact"  # Compact view for small displays


class PlayerScoreDisplay(BaseModel):
    """Player score display information"""
    player_id: str = Field(..., description="Player ID")
    full_name: str = Field(..., description="Full player name")
    abbreviated_name: Optional[str] = Field(None, description="Abbreviated name (e.g., R. FEDERER)")
    ranking: Optional[int] = Field(None, description="Player ranking")
    country_code: Optional[str] = Field(None, description="ISO country code (e.g., SUI)")
    photo_url: Optional[str] = Field(None, description="Player photo URL")

    # Current score
    points: str = Field(default="0", description="Current game points (0, 15, 30, 40, AD)")
    games: int = Field(default=0, description="Games won in current set")
    sets: int = Field(default=0, description="Sets won")

    # Serving indicator
    is_serving: bool = Field(default=False, description="Whether player is currently serving")

    def generate_abbreviated_name(self) -> str:
        """
        Generate abbreviated name from full name
        Format: First initial(s) + LAST NAME
        Examples:
        - Roger Federer → R. FEDERER
        - Rafael Nadal → R. NADAL
        - Juan Martin del Potro → J.M. DEL POTRO
        """
        if not self.full_name:
            return ""

        parts = self.full_name.strip().split()
        if len(parts) == 0:
            return ""

        if len(parts) == 1:
            return parts[0].upper()

        # Get initials from all but last part
        initials = [part[0].upper() + "." for part in parts[:-1]]

        # Last part in uppercase
        last_name = parts[-1].upper()

        return " ".join(initials) + " " + last_name

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-generate abbreviated name if not provided
        if not self.abbreviated_name and self.full_name:
            self.abbreviated_name = self.generate_abbreviated_name()


class SetScoreDisplay(BaseModel):
    """Set score display for completed sets"""
    set_number: int = Field(..., description="Set number (1-5)")
    player1_games: int = Field(..., description="Player 1 games won")
    player2_games: int = Field(..., description="Player 2 games won")
    tiebreak_score: Optional[tuple[int, int]] = Field(None, description="Tiebreak score if applicable")

    def format_score(self, player_num: int) -> str:
        """
        Format score for display
        Returns string like "6" or "7⁶" (superscript for tiebreak)
        """
        games = self.player1_games if player_num == 1 else self.player2_games

        if self.tiebreak_score:
            tb_score = self.tiebreak_score[player_num - 1]
            return f"{games}⁽{tb_score}⁾"

        return str(games)


class Scoreboard(BaseModel):
    """
    Complete scoreboard for match display
    """
    match_id: str = Field(..., description="Match ID")
    style: ScoreboardStyle = Field(default=ScoreboardStyle.TRADITIONAL, description="Display style")

    # Players
    player1: PlayerScoreDisplay = Field(..., description="Player 1 display info")
    player2: PlayerScoreDisplay = Field(..., description="Player 2 display info")

    # Match info
    match_format: str = Field(default="best_of_3", description="Match format")
    current_set: int = Field(default=1, description="Current set number")

    # Completed sets
    completed_sets: List[SetScoreDisplay] = Field(default_factory=list, description="Completed sets")

    # Match status
    is_complete: bool = Field(default=False, description="Whether match is complete")
    winner_player_id: Optional[str] = Field(None, description="Winner player ID")

    def update_from_match(self, match_score: dict):
        """
        Update scoreboard from match score data
        Synchronizes scoreboard with current match state

        Args:
            match_score: Dict with match score data from ScoringService.get_current_score_display()
        """
        # Update match status
        self.is_complete = match_score.get("is_complete", False)
        self.winner_player_id = match_score.get("winner_player_id")

        # Update completed sets
        self.completed_sets = []
        for i, set_data in enumerate(match_score.get("sets", [])):
            set_display = SetScoreDisplay(
                set_number=i + 1,
                player1_games=set_data["player1_games"],
                player2_games=set_data["player2_games"],
                tiebreak_score=set_data.get("tiebreak")
            )
            self.completed_sets.append(set_display)

        # Update current set and game scores
        current_set = match_score.get("current_set")
        current_game = match_score.get("current_game")

        if current_set:
            self.player1.games = current_set["player1_games"]
            self.player2.games = current_set["player2_games"]
            self.current_set = len(self.completed_sets) + 1

        if current_game:
            self.player1.points = current_game["player1_points"]
            self.player2.points = current_game["player2_points"]

        # Update sets won
        self.player1.sets = sum(
            1 for s in self.completed_sets
            if s.player1_games > s.player2_games
        )
        self.player2.sets = sum(
            1 for s in self.completed_sets
            if s.player2_games > s.player1_games
        )

        # Update serving indicator
        current_server = match_score.get("current_server_id")
        self.player1.is_serving = (current_server == self.player1.player_id)
        self.player2.is_serving = (current_server == self.player2.player_id)

    def to_display_dict(self) -> dict:
        """
        Convert scoreboard to display-friendly dict
        Format optimized for frontend rendering
        """
        return {
            "match_id": self.match_id,
            "style": self.style.value,
            "players": [
                {
                    "player_id": self.player1.player_id,
                    "name": self.player1.abbreviated_name or self.player1.full_name,
                    "full_name": self.player1.full_name,
                    "ranking": self.player1.ranking,
                    "country_code": self.player1.country_code,
                    "photo_url": self.player1.photo_url,
                    "score": {
                        "points": self.player1.points,
                        "games": self.player1.games,
                        "sets": self.player1.sets
                    },
                    "is_serving": self.player1.is_serving
                },
                {
                    "player_id": self.player2.player_id,
                    "name": self.player2.abbreviated_name or self.player2.full_name,
                    "full_name": self.player2.full_name,
                    "ranking": self.player2.ranking,
                    "country_code": self.player2.country_code,
                    "photo_url": self.player2.photo_url,
                    "score": {
                        "points": self.player2.points,
                        "games": self.player2.games,
                        "sets": self.player2.sets
                    },
                    "is_serving": self.player2.is_serving
                }
            ],
            "completed_sets": [
                {
                    "set_number": s.set_number,
                    "scores": [
                        s.format_score(1),
                        s.format_score(2)
                    ]
                }
                for s in self.completed_sets
            ],
            "match_info": {
                "format": self.match_format,
                "current_set": self.current_set,
                "is_complete": self.is_complete,
                "winner_player_id": self.winner_player_id
            }
        }
