"""
Scoring service - Implements official ATP/WTA tennis scoring rules
"""

from typing import Optional, Dict, List
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scoring import (
    MatchScore,
    MatchFormat,
    GameScore,
    SetScore,
    ScoreUpdate,
    GameSituation,
    LiveBroadcastData
)
from app.models.scoreboard import (
    Scoreboard,
    PlayerScoreDisplay,
    ScoreboardStyle
)
from app.models.sql.match_score import MatchScoreSQL


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

    def __init__(self, db: AsyncSession):
        self.db = db

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
        data = match_score.model_dump()
        row = MatchScoreSQL(
            match_id=data["match_id"],
            player1_id=data["player1_id"],
            player2_id=data["player2_id"],
            format=data["format"],
            current_server_id=data["current_server_id"],
            is_complete=data["is_complete"],
            winner_player_id=data.get("winner_player_id"),
            score_data={
                "sets": data.get("sets", []),
                "current_set": data.get("current_set"),
                "current_game": data.get("current_game"),
            },
        )
        self.db.add(row)
        await self.db.flush()

        return match_score

    async def get_match_score(self, match_id: str) -> Optional[MatchScore]:
        """Get match score by match ID"""
        result = await self.db.execute(
            select(MatchScoreSQL).where(MatchScoreSQL.match_id == match_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None

        score_data = row.score_data or {}
        return MatchScore(
            match_id=row.match_id,
            player1_id=row.player1_id,
            player2_id=row.player2_id,
            format=row.format,
            current_server_id=row.current_server_id,
            is_complete=row.is_complete,
            winner_player_id=row.winner_player_id,
            sets=score_data.get("sets", []),
            current_set=score_data.get("current_set"),
            current_game=score_data.get("current_game"),
        )

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

        # Get current game situation
        situation = self._get_game_situation(match_score)

        # Update in database
        result = await self.db.execute(
            select(MatchScoreSQL).where(MatchScoreSQL.match_id == match_id)
        )
        row = result.scalar_one_or_none()
        if row:
            data = match_score.model_dump()
            row.current_server_id = data["current_server_id"]
            row.is_complete = data["is_complete"]
            row.winner_player_id = data.get("winner_player_id")
            row.score_data = {
                "sets": data.get("sets", []),
                "current_set": data.get("current_set"),
                "current_game": data.get("current_game"),
            }
            await self.db.flush()

        return ScoreUpdate(
            match_id=match_id,
            point_winner_id=winner_player_id,
            timestamp=datetime.utcnow().isoformat(),
            events=events,
            situation=situation
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
        result = await self.db.execute(
            delete(MatchScoreSQL).where(MatchScoreSQL.match_id == match_id)
        )
        await self.db.flush()
        return result.rowcount > 0

    async def create_scoreboard(
        self,
        match_id: str,
        player1_name: str,
        player2_name: str,
        player1_ranking: Optional[int] = None,
        player2_ranking: Optional[int] = None,
        player1_country: Optional[str] = None,
        player2_country: Optional[str] = None,
        style: ScoreboardStyle = ScoreboardStyle.TRADITIONAL
    ) -> Scoreboard:
        """
        Create a scoreboard for visual display

        Args:
            match_id: Match ID
            player1_name: Player 1 full name
            player2_name: Player 2 full name
            player1_ranking: Player 1 ranking (optional)
            player2_ranking: Player 2 ranking (optional)
            player1_country: Player 1 country code (optional)
            player2_country: Player 2 country code (optional)
            style: Scoreboard style

        Returns:
            Scoreboard object
        """
        # Get match score to extract player IDs
        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        # Create player displays
        player1 = PlayerScoreDisplay(
            player_id=match_score.player1_id,
            full_name=player1_name,
            ranking=player1_ranking,
            country_code=player1_country
        )

        player2 = PlayerScoreDisplay(
            player_id=match_score.player2_id,
            full_name=player2_name,
            ranking=player2_ranking,
            country_code=player2_country
        )

        # Create scoreboard
        scoreboard = Scoreboard(
            match_id=match_id,
            style=style,
            player1=player1,
            player2=player2,
            match_format=match_score.format.value
        )

        # Update with current match state
        score_display = await self.get_current_score_display(match_id)
        scoreboard.update_from_match(score_display)

        return scoreboard

    async def get_scoreboard(
        self,
        match_id: str,
        player1_name: str,
        player2_name: str,
        style: ScoreboardStyle = ScoreboardStyle.TRADITIONAL,
        player1_ranking: Optional[int] = None,
        player2_ranking: Optional[int] = None,
        player1_country: Optional[str] = None,
        player2_country: Optional[str] = None
    ) -> dict:
        """
        Get scoreboard in display format

        Returns:
            Dict optimized for frontend rendering
        """
        scoreboard = await self.create_scoreboard(
            match_id=match_id,
            player1_name=player1_name,
            player2_name=player2_name,
            player1_ranking=player1_ranking,
            player2_ranking=player2_ranking,
            player1_country=player1_country,
            player2_country=player2_country,
            style=style
        )

        return scoreboard.to_display_dict()

    def _is_break_point(self, match_score: MatchScore) -> tuple[bool, Optional[str]]:
        """
        Check if current situation is a break point
        Break point = receiver is one point away from winning server's game

        Returns:
            Tuple (is_break_point, break_point_player_id)
        """
        if not match_score.current_game or match_score.current_game.is_complete:
            return False, None

        if match_score.current_game.is_tiebreak:
            return False, None  # No break points in tiebreak

        server_id = match_score.current_server_id
        receiver_id = match_score.player2_id if server_id == match_score.player1_id else match_score.player1_id

        # Check if receiver is one point from winning
        if server_id == match_score.player1_id:
            server_points = match_score.current_game.player1_points
            receiver_points = match_score.current_game.player2_points
        else:
            server_points = match_score.current_game.player2_points
            receiver_points = match_score.current_game.player1_points

        # Break point scenarios:
        # 1. Receiver has 40, server has < 40 (0, 15, 30)
        # 2. Receiver has advantage (deuce situation)
        if receiver_points >= 3:
            if server_points < 3:
                return True, receiver_id  # 40-0, 40-15, 40-30
            elif receiver_points > server_points:
                return True, receiver_id  # Advantage receiver

        return False, None

    def _is_set_point(self, match_score: MatchScore) -> tuple[bool, Optional[str]]:
        """
        Check if current situation is a set point
        Set point = player is one point away from winning the set

        Returns:
            Tuple (is_set_point, set_point_player_id)
        """
        if not match_score.current_game or not match_score.current_set:
            return False, None

        if match_score.current_game.is_complete:
            return False, None

        player1_games = match_score.current_set.player1_games
        player2_games = match_score.current_set.player2_games

        # Check each player for set point opportunity
        for player_id in [match_score.player1_id, match_score.player2_id]:
            is_player1 = player_id == match_score.player1_id
            player_games = player1_games if is_player1 else player2_games
            opponent_games = player2_games if is_player1 else player1_games
            player_points = match_score.current_game.player1_points if is_player1 else match_score.current_game.player2_points
            opponent_points = match_score.current_game.player2_points if is_player1 else match_score.current_game.player1_points

            # Set point scenarios:
            # 1. Leading 5-x and one point from game (regular set)
            # 2. In tiebreak at 6-6, leading in tiebreak points >= 6 with 1-point lead

            if match_score.current_game.is_tiebreak:
                # Tiebreak at 6-6: need 7+ points with 2-point lead
                if player_points >= 6 and player_points > opponent_points:
                    # One point away from winning tiebreak (would be 2-point lead)
                    if player_points - opponent_points == 1:
                        return True, player_id
            else:
                # Regular game: player has 5+ games and is one point from winning game
                if player_games >= 5:
                    # Check if one point from game
                    if player_points >= 3:
                        if opponent_points < 3:
                            return True, player_id  # 40-0, 40-15, 40-30
                        elif player_points > opponent_points:
                            return True, player_id  # Advantage

        return False, None

    def _is_match_point(self, match_score: MatchScore) -> tuple[bool, Optional[str]]:
        """
        Check if current situation is a match point
        Match point = player is one point away from winning the match

        Returns:
            Tuple (is_match_point, match_point_player_id)
        """
        is_set_point, set_point_player_id = self._is_set_point(match_score)

        if not is_set_point:
            return False, None

        # Check if winning this set would win the match
        sets_needed = 3 if match_score.format == MatchFormat.BEST_OF_5 else 2
        player_sets = match_score.get_sets_won(set_point_player_id)

        # If player already has (sets_needed - 1) sets, this is match point
        if player_sets >= sets_needed - 1:
            return True, set_point_player_id

        return False, None

    def _get_game_situation(self, match_score: MatchScore) -> GameSituation:
        """
        Get comprehensive game situation analysis

        Returns:
            GameSituation object with all situation flags
        """
        situation = GameSituation()

        if not match_score.current_game or match_score.current_game.is_complete:
            return situation

        # Check special situations
        is_break_point, break_point_player_id = self._is_break_point(match_score)
        is_set_point, set_point_player_id = self._is_set_point(match_score)
        is_match_point, match_point_player_id = self._is_match_point(match_score)

        situation.is_break_point = is_break_point
        situation.break_point_player_id = break_point_player_id
        situation.is_set_point = is_set_point
        situation.set_point_player_id = set_point_player_id
        situation.is_match_point = is_match_point
        situation.match_point_player_id = match_point_player_id

        # Check deuce/advantage
        if not match_score.current_game.is_tiebreak:
            p1_points = match_score.current_game.player1_points
            p2_points = match_score.current_game.player2_points

            if p1_points >= 3 and p2_points >= 3:
                if p1_points == p2_points:
                    situation.is_deuce = True
                else:
                    situation.is_advantage = True
                    situation.advantage_player_id = match_score.player1_id if p1_points > p2_points else match_score.player2_id

        # Check tiebreak
        situation.is_tiebreak = match_score.current_game.is_tiebreak

        # Check bagel/breadstick possibilities
        if match_score.current_set:
            p1_games = match_score.current_set.player1_games
            p2_games = match_score.current_set.player2_games

            # Bagel: 5-0 or 0-5 (possible 6-0)
            if (p1_games == 5 and p2_games == 0) or (p1_games == 0 and p2_games == 5):
                situation.is_bagel_possible = True

            # Breadstick: 5-1 or 1-5 (possible 6-1)
            if (p1_games == 5 and p2_games == 1) or (p1_games == 1 and p2_games == 5):
                situation.is_breadstick_possible = True

        # Build situation text
        text_parts = []

        if situation.is_match_point:
            text_parts.append("MATCH POINT")
        elif situation.is_set_point:
            text_parts.append("SET POINT")

        if situation.is_break_point:
            text_parts.append("BREAK POINT")

        if situation.is_deuce:
            text_parts.append("DEUCE")
        elif situation.is_advantage:
            text_parts.append("ADVANTAGE")

        if situation.is_tiebreak:
            text_parts.insert(0, "TIE-BREAK")

        if situation.is_bagel_possible:
            text_parts.append("BAGEL THREAT (6-0)")
        elif situation.is_breadstick_possible:
            text_parts.append("BREADSTICK THREAT (6-1)")

        situation.situation_text = " | ".join(text_parts) if text_parts else "IN PLAY"

        return situation

    async def get_game_situation(self, match_id: str) -> GameSituation:
        """
        Get current game situation with all special conditions

        Args:
            match_id: Match ID

        Returns:
            GameSituation object
        """
        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        return self._get_game_situation(match_score)

    async def get_live_broadcast_data(
        self,
        match_id: str,
        player1_name: str,
        player2_name: str,
        player1_ranking: Optional[int] = None,
        player2_ranking: Optional[int] = None,
        player1_country: Optional[str] = None,
        player2_country: Optional[str] = None,
        last_points_count: int = 5
    ) -> LiveBroadcastData:
        """
        Get optimized data package for live broadcast/streaming

        Combines scoreboard, situation, recent points, and key stats
        in a single optimized response for minimal latency.

        Args:
            match_id: Match ID
            player1_name: Player 1 name
            player2_name: Player 2 name
            player1_ranking: Player 1 ranking (optional)
            player2_ranking: Player 2 ranking (optional)
            player1_country: Player 1 country code (optional)
            player2_country: Player 2 country code (optional)
            last_points_count: Number of recent points to include (default: 5)

        Returns:
            LiveBroadcastData with all broadcast info
        """
        from app.services.point_history_service import PointHistoryService

        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        # Get scoreboard (compact format)
        scoreboard = await self.get_scoreboard(
            match_id=match_id,
            player1_name=player1_name,
            player2_name=player2_name,
            player1_ranking=player1_ranking,
            player2_ranking=player2_ranking,
            player1_country=player1_country,
            player2_country=player2_country
        )

        # Get situation
        situation = self._get_game_situation(match_score)

        # Get last points from history
        point_service = PointHistoryService(self.db)
        all_points = await point_service.get_points_by_match(match_id)
        last_points = all_points[-last_points_count:] if len(all_points) >= last_points_count else all_points

        # Format last points for broadcast (compact)
        last_points_summary = []
        for point in last_points:
            last_points_summary.append({
                "winner_id": point.point_winner_id,
                "score": point.score_after_point,
                "outcome": point.outcome,
                "is_break_point": point.is_break_point
            })

        # Get key stats
        stats = await self.get_match_stats(match_id)
        summary = await point_service.get_match_summary(match_id)

        key_stats = {
            "sets_won": stats["sets_won"],
            "games_won": stats["games_won"],
            "aces": summary.aces_count,
            "double_faults": summary.double_faults_count,
            "winners": summary.winners_count,
            "unforced_errors": summary.unforced_errors_count,
            "break_points": {
                "total": summary.break_points_total,
                "converted": summary.break_points_converted
            }
        }

        return LiveBroadcastData(
            match_id=match_id,
            scoreboard=scoreboard,
            situation=situation,
            last_points=last_points_summary,
            key_stats=key_stats,
            timestamp=datetime.utcnow().isoformat()
        )

    async def get_broadcast_score(self, match_id: str) -> Dict[str, any]:
        """
        Get minimal score data optimized for broadcast overlay

        Returns only essential info for TV/streaming overlay:
        - Current game score
        - Sets won
        - Current set games
        - Server indicator

        Args:
            match_id: Match ID

        Returns:
            Compact dict with broadcast score
        """
        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        # Get game score
        current_game_score = None
        if match_score.current_game:
            p1_score, p2_score = match_score.current_game.get_score_display()
            current_game_score = {
                "p1": p1_score,
                "p2": p2_score,
                "tiebreak": match_score.current_game.is_tiebreak
            }

        # Get sets won
        p1_sets = sum(1 for s in match_score.sets if s.winner_player_id == match_score.player1_id)
        p2_sets = sum(1 for s in match_score.sets if s.winner_player_id == match_score.player2_id)

        # Get current set games
        current_set_games = None
        if match_score.current_set:
            current_set_games = {
                "p1": match_score.current_set.player1_games,
                "p2": match_score.current_set.player2_games
            }

        # Get all completed sets
        completed_sets = []
        for set_score in match_score.sets:
            completed_sets.append({
                "p1": set_score.player1_games,
                "p2": set_score.player2_games,
                "tiebreak": set_score.tiebreak_score
            })

        return {
            "match_id": match_id,
            "game": current_game_score,
            "sets": {
                "p1": p1_sets,
                "p2": p2_sets
            },
            "current_set": current_set_games,
            "completed_sets": completed_sets,
            "server": "p1" if match_score.current_server_id == match_score.player1_id else "p2",
            "complete": match_score.is_complete
        }

    async def export_complete_match_data(self, match_id: str) -> Dict[str, any]:
        """
        Export complete match data for analysis/archival

        Includes:
        - Full match score
        - All point history
        - Complete statistics
        - Timeline of events

        Args:
            match_id: Match ID

        Returns:
            Complete match data package
        """
        from app.services.point_history_service import PointHistoryService

        match_score = await self.get_match_score(match_id)
        if not match_score:
            raise ValueError(f"Match score not found for match_id: {match_id}")

        # Get all points
        point_service = PointHistoryService(self.db)
        all_points = await point_service.get_points_by_match(match_id)
        summary = await point_service.get_match_summary(match_id)

        # Get stats
        stats = await self.get_match_stats(match_id)

        # Build timeline of key events
        timeline = []
        for point in all_points:
            if point.is_break_point or point.is_set_point or point.is_match_point:
                timeline.append({
                    "set": point.set_number,
                    "game": point.game_number,
                    "point": point.point_number,
                    "type": "break_point" if point.is_break_point else ("match_point" if point.is_match_point else "set_point"),
                    "winner": point.point_winner_id,
                    "score": point.score_after_point
                })

        return {
            "match_id": match_id,
            "format": match_score.format.value,
            "winner": match_score.winner_player_id,
            "is_complete": match_score.is_complete,
            "score": {
                "sets": [s.model_dump() for s in match_score.sets],
                "current_set": match_score.current_set.model_dump() if match_score.current_set else None
            },
            "statistics": {
                "match_stats": stats,
                "point_summary": summary.model_dump()
            },
            "points": [p.model_dump() for p in all_points],
            "timeline": timeline,
            "export_timestamp": datetime.utcnow().isoformat()
        }
