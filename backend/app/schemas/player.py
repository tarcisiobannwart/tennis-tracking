"""
Player Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class PlayerBase(BaseModel):
    """Base player schema"""
    name: str
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    country: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    dominant_hand: Optional[str] = None
    ranking: Optional[int] = None
    skill_level: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

    @validator("dominant_hand")
    def validate_dominant_hand(cls, v):
        if v and v not in ["right", "left", "ambidextrous"]:
            raise ValueError("dominant_hand must be 'right', 'left', or 'ambidextrous'")
        return v

    @validator("skill_level")
    def validate_skill_level(cls, v):
        if v and v not in ["beginner", "intermediate", "advanced", "professional"]:
            raise ValueError("skill_level must be 'beginner', 'intermediate', 'advanced', or 'professional'")
        return v

    @validator("country")
    def validate_country(cls, v):
        if v and len(v) != 3:
            raise ValueError("country must be a 3-letter ISO code")
        return v

    @validator("age")
    def validate_age(cls, v):
        if v and (v < 5 or v > 100):
            raise ValueError("age must be between 5 and 100")
        return v


class PlayerCreate(PlayerBase):
    """Schema for creating a player"""
    pass


class PlayerUpdate(BaseModel):
    """Schema for updating a player"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    country: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    dominant_hand: Optional[str] = None
    ranking: Optional[int] = None
    skill_level: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = None


class PlayerResponse(PlayerBase):
    """Schema for player response"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlayerStats(BaseModel):
    """Schema for player statistics"""
    player_id: str
    total_matches: int
    wins: int
    losses: int
    win_percentage: float
    total_sets_played: int
    sets_won: int
    sets_lost: int
    total_games_played: int
    games_won: int
    games_lost: int
    total_points_played: int
    points_won: int
    points_lost: int
    aces: int
    double_faults: int
    first_serve_percentage: float
    first_serve_points_won: float
    second_serve_points_won: float
    break_points_saved: float
    break_points_converted: float
    winners: int
    unforced_errors: int
    forced_errors: int
    average_rally_length: float
    longest_rally: int
    average_match_duration: Optional[float] = None
    recent_form: List[str] = []  # ["W", "L", "W", "W", "L"]

    class Config:
        from_attributes = True


class PlayerProfile(PlayerResponse):
    """Extended player profile with statistics"""
    stats: Optional[PlayerStats] = None
    recent_matches: List[str] = []  # Match IDs
    upcoming_matches: List[str] = []  # Match IDs

    class Config:
        from_attributes = True