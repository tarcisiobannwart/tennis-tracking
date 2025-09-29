"""
Match Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MatchStatusEnum(str, Enum):
    """Match status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class MatchTypeEnum(str, Enum):
    """Match type enumeration"""
    SINGLES = "singles"
    DOUBLES = "doubles"


class SurfaceEnum(str, Enum):
    """Court surface enumeration"""
    CLAY = "clay"
    GRASS = "grass"
    HARD = "hard"
    CARPET = "carpet"


class MatchBase(BaseModel):
    """Base match schema"""
    title: str
    match_type: MatchTypeEnum = MatchTypeEnum.SINGLES
    surface: Optional[SurfaceEnum] = None
    tournament_name: Optional[str] = None
    round_name: Optional[str] = None
    best_of_sets: int = 3
    tiebreak_at: int = 6
    scheduled_at: Optional[datetime] = None
    venue: Optional[str] = None
    court_number: Optional[str] = None
    weather_conditions: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    is_public: bool = True

    @validator("best_of_sets")
    def validate_best_of_sets(cls, v):
        if v not in [3, 5]:
            raise ValueError("best_of_sets must be 3 or 5")
        return v

    @validator("tiebreak_at")
    def validate_tiebreak_at(cls, v):
        if v < 6:
            raise ValueError("tiebreak_at must be at least 6")
        return v


class MatchCreate(MatchBase):
    """Schema for creating a match"""
    player1_id: str
    player2_id: str

    @validator("player2_id")
    def validate_different_players(cls, v, values):
        if "player1_id" in values and v == values["player1_id"]:
            raise ValueError("player1_id and player2_id must be different")
        return v


class MatchUpdate(BaseModel):
    """Schema for updating a match"""
    title: Optional[str] = None
    match_type: Optional[MatchTypeEnum] = None
    surface: Optional[SurfaceEnum] = None
    tournament_name: Optional[str] = None
    round_name: Optional[str] = None
    best_of_sets: Optional[int] = None
    tiebreak_at: Optional[int] = None
    status: Optional[MatchStatusEnum] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    venue: Optional[str] = None
    court_number: Optional[str] = None
    weather_conditions: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    is_public: Optional[bool] = None


class MatchResponse(MatchBase):
    """Schema for match response"""
    id: str
    player1_id: str
    player2_id: str
    player1_sets: int
    player2_sets: int
    current_set: int
    status: MatchStatusEnum
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    video_file_path: Optional[str] = None
    analysis_status: str
    analysis_progress: int
    analysis_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MatchStats(BaseModel):
    """Schema for match statistics"""
    match_id: str

    # Overall match stats
    duration_minutes: Optional[int] = None
    total_points: int
    total_games: int
    total_sets: int

    # Player 1 stats
    player1_stats: Dict[str, Any] = {}

    # Player 2 stats
    player2_stats: Dict[str, Any] = {}

    # Set by set breakdown
    set_scores: List[Dict[str, Any]] = []

    # Key moments
    key_moments: List[Dict[str, Any]] = []

    # Performance insights
    insights: List[str] = []

    class Config:
        from_attributes = True


class MatchEventSummary(BaseModel):
    """Schema for match event summary"""
    match_id: str
    events: List[Dict[str, Any]] = []
    points: List[Dict[str, Any]] = []
    games: List[Dict[str, Any]] = []
    sets: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class MatchWithPlayers(MatchResponse):
    """Match response with player details"""
    player1: Dict[str, Any]
    player2: Dict[str, Any]

    class Config:
        from_attributes = True