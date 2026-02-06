"""
Point history models for detailed point tracking
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PointOutcome(str, Enum):
    """Point outcome types"""
    ACE = "ace"
    WINNER = "winner"
    UNFORCED_ERROR = "unforced_error"
    FORCED_ERROR = "forced_error"
    DOUBLE_FAULT = "double_fault"
    SERVICE_WINNER = "service_winner"
    RETURN_WINNER = "return_winner"
    VOLLEY_WINNER = "volley_winner"
    SMASH_WINNER = "smash_winner"
    DROP_SHOT_WINNER = "drop_shot_winner"
    LET = "let"
    NET = "net"
    OUT = "out"
    LONG = "long"
    WIDE = "wide"


class PointDetails(BaseModel):
    """
    Detailed information about a single point
    Contains 15+ fields for comprehensive analysis
    """
    # Identifiers
    point_id: str = Field(..., description="Unique point ID")
    match_id: str = Field(..., description="Match ID")
    set_number: int = Field(..., description="Set number (1-5)")
    game_number: int = Field(..., description="Game number in set")
    point_number: int = Field(..., description="Point number in game")

    # Score context
    score_before: Dict[str, str] = Field(..., description="Score before point (e.g., {'player1': '30', 'player2': '15'})")
    score_after: Dict[str, str] = Field(..., description="Score after point")
    set_score_before: Dict[str, int] = Field(..., description="Set score before point (games)")
    set_score_after: Dict[str, int] = Field(..., description="Set score after point (games)")

    # Players
    server_player_id: str = Field(..., description="Server player ID")
    receiver_player_id: str = Field(..., description="Receiver player ID")
    point_winner_id: str = Field(..., description="Point winner player ID")

    # Point outcome
    outcome: PointOutcome = Field(..., description="How the point ended")
    winning_shot: Optional[str] = Field(None, description="Type of winning shot")
    error_type: Optional[str] = Field(None, description="Type of error if applicable")

    # Rally information
    rally_length: int = Field(default=0, description="Number of shots in rally")
    rally_duration: Optional[float] = Field(None, description="Rally duration in seconds")

    # Serve information
    is_first_serve: bool = Field(default=True, description="Whether this was a first serve")
    serve_speed: Optional[float] = Field(None, description="Serve speed in km/h")
    serve_placement: Optional[str] = Field(None, description="Serve placement (wide, body, T)")
    is_serve_in: bool = Field(default=True, description="Whether serve was in")

    # Strategic context
    is_break_point: bool = Field(default=False, description="Whether this was a break point")
    is_set_point: bool = Field(default=False, description="Whether this was a set point")
    is_match_point: bool = Field(default=False, description="Whether this was a match point")
    is_game_point: bool = Field(default=False, description="Whether this was a game point")

    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When point occurred")
    video_timestamp: Optional[float] = Field(None, description="Video timestamp in seconds")

    # Additional data
    court_position_data: Optional[Dict[str, Any]] = Field(None, description="Player positions during point")
    ball_trajectory_data: Optional[Dict[str, Any]] = Field(None, description="Ball trajectory data")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        use_enum_values = True


class PointHistoryFilter(BaseModel):
    """Filter for querying point history"""
    match_id: Optional[str] = None
    player_id: Optional[str] = None
    set_number: Optional[int] = None
    outcome: Optional[PointOutcome] = None
    is_break_point: Optional[bool] = None
    is_set_point: Optional[bool] = None
    is_match_point: Optional[bool] = None
    min_rally_length: Optional[int] = None
    max_rally_length: Optional[int] = None


class PointHistorySummary(BaseModel):
    """Summary statistics for point history"""
    total_points: int
    points_by_outcome: Dict[str, int]
    average_rally_length: float
    break_points_total: int
    break_points_converted: int
    aces_count: int
    double_faults_count: int
    winners_count: int
    unforced_errors_count: int
