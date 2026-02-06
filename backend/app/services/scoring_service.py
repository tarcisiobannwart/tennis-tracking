"""
Scoring service - Implements official ATP/WTA tennis scoring rules
"""

from typing import Optional, Dict, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.scoring import (
    MatchScore,
    MatchFormat,
    GameScore,
    SetScore,
    ScoreUpdate
)
from app.core.mongodb import get_database


class ScoringService:
    """
    Service for managing tennis match scoring
    Implements official ATP/WTA rules:
    - Points: 0, 15, 30, 40, Deuce, Advantage
    - Games: First to 4 points, win by 2
    - Sets: First to 6 games, win by 2 (or tiebreak at 6-6)
    - Tiebreak: First to 7 points, win by 2
    - Match: Best of 3 or Best of 5 sets
    - Server alternates each game (and every 2 points in tiebreak)
    """

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db or get_database()
        self.collection = self.db.get_collection("match_scores")

    async def create_match_score(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
        format: MatchFormat = MatchFormat.BEST_OF_3,
        starting_server_id: Optional[str] = None
    ) -> MatchScore:
        """
        Create a new match score

        Args:
            match_id: Match ID
            player1_id: Player 1 ID
            player2_id: Player 2 ID
            format: Match format (best_of_3 or best_of_5)
            starting_server_id: ID of player who serves first (defaults to player1)

        Returns:
            MatchScore object
        """
        server_id = starting_server_id or player1_id

        match_score = MatchScore(
            match_id=match_id,
            player1_id=player1_id,
            player2_id=player2_id,
            format=format,
            current_server_id=server_id
        )

        # Initialize first set and game
        match_score.start_new_set()
        match_score.start_new_game()

        # Save to database
        await self.collection.insert_one(match_score.model_dump())

        return match_score

    async def get_match_score(self, match_id: str) -> Optional[MatchScore]:
        """Get match score by match ID"""
        score_data = await self.collection.find_one({"match_id": match_id})
        if not score_data:
            return None

        # Remove MongoDB _id field
        score_data.pop("_id", None)
        return MatchScore(**score_data)

    async def add_point(self, match_id: str, winner_player_id: str) -> ScoreUpdate:
        """
        Add a point to the match
        Implements full ATP/WTA scoring logic including:
        - Point progression (0 → 15 → 30 → 40 → game)
        - Deuce and advantage rules
        - Tiebreak rules (first to 7, win by 2)
        - Set completion (first to 6 games, win by 2)
        - Match completion (best of 3/5)
        - Server alternation

        Args:
            match_id: Match ID
            winner_player_id: ID of player who won the point

        Returns:
            ScoreUpdate with events (point_won, game_won, set_won, match_won)
        """
        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        if match_score.is_complete:
            raise ValueError(f"Match {match_id} is already complete")

        # Validate winner is a valid player
        if winner_player_id not in [match_score.player1_id, match_score.player2_id]:
            raise ValueError(f"Invalid player ID: {winner_player_id}")

        # Add point and get events
        events = match_score.add_point(winner_player_id)

        # Update in database
        await self.collection.update_one(
            {"match_id": match_id},
            {"$set": match_score.model_dump()}
        )

        return ScoreUpdate(
            match_id=match_id,
            point_winner_id=winner_player_id,
            timestamp=datetime.utcnow().isoformat(),
            events=events
        )

    async def get_current_score_display(self, match_id: str) -> Dict[str, any]:
        """
        Get current score in display format

        Returns:
            Dict with formatted score including:
            - sets: List of set scores
            - current_set: Current set score
            - current_game: Current game score (0, 15, 30, 40, AD)
            - server: Current server ID
        """
        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        # Build sets display
        sets_display = []
        for set_score in match_score.sets:
            set_dict = {
                "player1_games": set_score.player1_games,
                "player2_games": set_score.player2_games,
                "tiebreak": set_score.tiebreak_score
            }
            sets_display.append(set_dict)

        # Current set
        current_set_display = None
        if match_score.current_set:
            current_set_display = {
                "player1_games": match_score.current_set.player1_games,
                "player2_games": match_score.current_set.player2_games
            }

        # Current game score
        current_game_display = None
        if match_score.current_game:
            p1_score, p2_score = match_score.current_game.get_score_display()
            current_game_display = {
                "player1_points": p1_score,
                "player2_points": p2_score,
                "is_tiebreak": match_score.current_game.is_tiebreak
            }

        return {
            "match_id": match_id,
            "player1_id": match_score.player1_id,
            "player2_id": match_score.player2_id,
            "sets": sets_display,
            "current_set": current_set_display,
            "current_game": current_game_display,
            "current_server_id": match_score.current_server_id,
            "is_complete": match_score.is_complete,
            "winner_player_id": match_score.winner_player_id
        }

    async def get_match_stats(self, match_id: str) -> Dict[str, any]:
        """
        Get match statistics

        Returns:
            Dict with stats including:
            - sets_won: Sets won by each player
            - games_won: Total games won
            - current_set_number: Current set number
        """
        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        player1_sets = sum(1 for s in match_score.sets if s.winner_player_id == match_score.player1_id)
        player2_sets = sum(1 for s in match_score.sets if s.winner_player_id == match_score.player2_id)

        player1_games = sum(s.player1_games for s in match_score.sets)
        player2_games = sum(s.player2_games for s in match_score.sets)

        if match_score.current_set:
            player1_games += match_score.current_set.player1_games
            player2_games += match_score.current_set.player2_games

        return {
            "match_id": match_id,
            "sets_won": {
                "player1": player1_sets,
                "player2": player2_sets
            },
            "games_won": {
                "player1": player1_games,
                "player2": player2_games
            },
            "current_set_number": len(match_score.sets) + (1 if match_score.current_set else 0),
            "match_format": match_score.format.value,
            "is_complete": match_score.is_complete
        }

    async def delete_match_score(self, match_id: str) -> bool:
        """Delete match score"""
        result = await self.collection.delete_one({"match_id": match_id})
        return result.deleted_count > 0
