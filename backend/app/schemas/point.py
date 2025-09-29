"""
Point Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class PointBase(BaseModel):
    """Base point schema"""
    point_number: int
    server_player_id: str
    outcome: Optional[str] = None
    winning_shot: Optional[str] = None
    rally_length: int = 0
    rally_duration: Optional[float] = None
    serve_speed: Optional[float] = None
    serve_placement: Optional[Dict[str, float]] = None
    first_serve_in: Optional[bool] = None
    second_serve: bool = False


class PointCreate(PointBase):
    """Schema for creating a point"""
    match_id: str
    set_id: str
    game_id: str
    score_before: Optional[Dict[str, str]] = None

    @validator("rally_length")
    def validate_rally_length(cls, v):
        if v < 0:
            raise ValueError("rally_length must be non-negative")
        return v


class PointResponse(PointBase):
    """Schema for point response"""
    id: str
    match_id: str
    set_id: str
    game_id: str
    winner_player_id: Optional[str] = None
    score_before: Optional[Dict[str, str]] = None
    ball_trajectory: Optional[List[Dict[str, float]]] = None
    bounce_points: Optional[List[Dict[str, float]]] = None
    player_positions: Optional[List[Dict[str, Any]]] = None
    video_start_time: Optional[float] = None
    video_end_time: Optional[float] = None
    analysis_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PointEvent(BaseModel):
    """Schema for point events (WebSocket)"""
    point_id: str
    match_id: str
    event_type: str  # "point_started", "point_scored", "serve", "shot"
    timestamp: datetime
    player_id: Optional[str] = None
    data: Dict[str, Any] = {}

    class Config:
        from_attributes = True