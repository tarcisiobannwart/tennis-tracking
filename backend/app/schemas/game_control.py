"""
Game Control Pydantic schemas
Schemas para controle de jogo em tempo real
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum


class GameStateEnum(str, Enum):
    """Game state enumeration"""
    WARM_UP = "warm_up"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"


class PointTypeEnum(str, Enum):
    """Point type enumeration"""
    ACE = "ace"
    WINNER = "winner"
    FORCED_ERROR = "forced_error"
    UNFORCED_ERROR = "unforced_error"
    DOUBLE_FAULT = "double_fault"
    RALLY = "rally"


class ShotTypeEnum(str, Enum):
    """Shot type enumeration"""
    SERVE = "serve"
    FOREHAND = "forehand"
    BACKHAND = "backhand"
    VOLLEY = "volley"
    SMASH = "smash"
    DROP_SHOT = "drop_shot"
    LOB = "lob"
    SLICE = "slice"


class GameEventTypeEnum(str, Enum):
    """Game event type enumeration"""
    MATCH_STARTED = "match_started"
    MATCH_PAUSED = "match_paused"
    MATCH_RESUMED = "match_resumed"
    MATCH_COMPLETED = "match_completed"
    POINT_SCORED = "point_scored"
    GAME_WON = "game_won"
    SET_WON = "set_won"
    BREAK_POINT = "break_point"
    GAME_POINT = "game_point"
    SET_POINT = "set_point"
    MATCH_POINT = "match_point"
    ACE = "ace"
    WINNER = "winner"
    DOUBLE_FAULT = "double_fault"


class StartMatchRequest(BaseModel):
    """Schema for starting a match"""
    match_id: str
    server_player_id: str
    tournament_data: Optional[Dict[str, Any]] = None

    @validator("tournament_data")
    def validate_tournament_data(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("tournament_data must be a dictionary")
        return v


class PauseMatchRequest(BaseModel):
    """Schema for pausing a match"""
    match_id: str
    reason: Optional[str] = None


class ResumeMatchRequest(BaseModel):
    """Schema for resuming a match"""
    match_id: str


class PointMetadata(BaseModel):
    """Metadata for a point"""
    ball_speed: Optional[float] = Field(None, description="Ball speed in km/h")
    ball_position: Optional[Dict[str, float]] = Field(None, description="Ball position (x, y)")
    shot_type: Optional[ShotTypeEnum] = None
    rally_length: Optional[int] = Field(None, ge=0, description="Number of shots in rally")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Point duration in seconds")
    additional_data: Optional[Dict[str, Any]] = None

    @validator("ball_position")
    def validate_ball_position(cls, v):
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError("ball_position must be a dictionary")
            if "x" not in v or "y" not in v:
                raise ValueError("ball_position must contain 'x' and 'y' keys")
        return v


class AddPointRequest(BaseModel):
    """Schema for adding a point"""
    match_id: str
    winner_player_id: str
    point_type: PointTypeEnum
    metadata: Optional[PointMetadata] = None


class GameStateSnapshot(BaseModel):
    """Snapshot of game state before a point"""
    match_id: str
    current_set: int
    current_game: int
    player1_sets: int
    player2_sets: int
    player1_games: int
    player2_games: int
    player1_points: int
    player2_points: int
    server_player_id: str
    timestamp: datetime


class GameControlResponse(BaseModel):
    """Response for game control operations"""
    success: bool
    message: str
    match_id: str
    state: Optional[GameStateEnum] = None
    data: Optional[Dict[str, Any]] = None


class RegisterCallbackRequest(BaseModel):
    """Schema for registering event callbacks"""
    match_id: str
    event_type: GameEventTypeEnum


class GameEventData(BaseModel):
    """Data for a game event"""
    match_id: str
    event_type: GameEventTypeEnum
    player_id: Optional[str] = None
    timestamp: datetime
    state_before: Optional[GameStateSnapshot] = None
    metadata: Optional[Dict[str, Any]] = None


class MatchStateResponse(BaseModel):
    """Current match state response"""
    match_id: str
    state: GameStateEnum
    current_set: int
    current_game: int
    player1_sets: int
    player2_sets: int
    player1_games: int
    player2_games: int
    player1_points: int
    player2_points: int
    server_player_id: str
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    last_point_at: Optional[datetime] = None
