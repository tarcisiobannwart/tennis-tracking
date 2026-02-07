"""
Pydantic schemas for ranking API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RankingTypeEnum(str, Enum):
    """Ranking type enumeration"""
    ROUND_ROBIN = "round_robin"
    CHALLENGE = "challenge"


class RankingStatusEnum(str, Enum):
    """Ranking status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


# Ranking Schemas
class RankingBase(BaseModel):
    """Base ranking schema"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    ranking_type: RankingTypeEnum = RankingTypeEnum.ROUND_ROBIN
    status: RankingStatusEnum = RankingStatusEnum.ACTIVE
    organization_id: Optional[str] = None
    venue: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    scoring_config: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_rounds: Optional[int] = None
    is_public: bool = True
    allow_self_scheduling: bool = False


class RankingCreate(RankingBase):
    """Schema for creating a ranking"""
    pass


class RankingUpdate(BaseModel):
    """Schema for updating a ranking"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[RankingStatusEnum] = None
    venue: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    scoring_config: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_rounds: Optional[int] = None
    current_round: Optional[int] = None
    is_public: Optional[bool] = None
    allow_self_scheduling: Optional[bool] = None


class RankingResponse(RankingBase):
    """Schema for ranking response"""
    id: str
    current_round: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    total_participants: Optional[int] = 0

    class Config:
        from_attributes = True


# Ranking Participant Schemas
class RankingParticipantCreate(BaseModel):
    """Schema for adding participant to ranking"""
    ranking_id: str
    user_id: str


class RankingParticipantResponse(BaseModel):
    """Schema for ranking participant response"""
    id: str
    ranking_id: str
    user_id: str
    is_active: bool
    joined_at: datetime
    position: Optional[int] = None
    points: float
    matches_played: int
    matches_won: int
    matches_lost: int
    matches_drawn: int
    sets_won: int
    sets_lost: int
    position_history: List[int] = []

    class Config:
        from_attributes = True


# Ranking Round Schemas
class RankingRoundCreate(BaseModel):
    """Schema for creating a ranking round"""
    ranking_id: str
    round_number: int
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class RankingRoundUpdate(BaseModel):
    """Schema for updating a ranking round"""
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_completed: Optional[bool] = None


class RankingRoundResponse(BaseModel):
    """Schema for ranking round response"""
    id: str
    ranking_id: str
    round_number: int
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_completed: bool
    total_matches: int = 0
    completed_matches: int = 0

    class Config:
        from_attributes = True


# Ranking Match Schemas
class RankingMatchCreate(BaseModel):
    """Schema for creating a ranking match"""
    ranking_id: str
    round_id: Optional[str] = None
    player1_id: str
    player2_id: str
    scheduled_at: Optional[datetime] = None


class RankingMatchUpdate(BaseModel):
    """Schema for updating a ranking match"""
    match_id: Optional[str] = None
    player1_score: Optional[str] = None
    player2_score: Optional[str] = None
    winner_id: Optional[str] = None
    player1_points: Optional[float] = None
    player2_points: Optional[float] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: Optional[str] = None


class RankingMatchResponse(BaseModel):
    """Schema for ranking match response"""
    id: str
    ranking_id: str
    round_id: Optional[str] = None
    player1_id: str
    player2_id: str
    player1_score: Optional[str] = None
    player2_score: Optional[str] = None
    winner_id: Optional[str] = None
    player1_points: float
    player2_points: float
    status: str
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Standings Schema
class StandingsEntry(BaseModel):
    """Single entry in standings table"""
    position: int
    previous_position: Optional[int] = None
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    points: float
    matches_played: int
    matches_won: int
    matches_lost: int
    matches_drawn: int
    sets_won: int
    sets_lost: int
    games_won: int
    games_lost: int
    win_rate: float
    set_ratio: float
    position_history: List[int] = []
    position_change: Optional[int] = None


class StandingsResponse(BaseModel):
    """Full standings response"""
    ranking_id: str
    current_round: int
    standings: List[StandingsEntry]
    updated_at: datetime


# List responses
class RankingListResponse(BaseModel):
    """Paginated list of rankings"""
    data: List[RankingResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class RankingDetailResponse(RankingResponse):
    """Detailed ranking with my stats"""
    total_participants: int
    my_position: Optional[int] = None
    my_stats: Optional[Dict[str, Any]] = None
