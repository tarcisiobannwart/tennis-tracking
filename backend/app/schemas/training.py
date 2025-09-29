"""
Training Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class DrillTypeResponse(BaseModel):
    """Schema for drill type response"""
    id: str
    name: str
    description: Optional[str] = None
    category: str
    difficulty: str
    duration_minutes: Optional[int] = None
    equipment_needed: Optional[List[str]] = None
    instructions: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrainingDrillCreate(BaseModel):
    """Schema for creating a training drill"""
    drill_type_id: str
    order_in_session: int
    duration_minutes: Optional[int] = None
    repetitions: Optional[int] = None
    sets: Optional[int] = None


class TrainingDrillResponse(TrainingDrillCreate):
    """Schema for training drill response"""
    id: str
    training_session_id: str
    success_rate: Optional[float] = None
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None
    accuracy_score: Optional[float] = None
    drill_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    notes: Optional[str] = None
    coach_feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrainingSessionCreate(BaseModel):
    """Schema for creating a training session"""
    player_id: str
    title: str
    description: Optional[str] = None
    session_type: str
    scheduled_at: datetime
    objectives: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None
    coach_name: Optional[str] = None

    @validator("session_type")
    def validate_session_type(cls, v):
        allowed_types = ["practice", "match_prep", "recovery", "fitness", "technique"]
        if v not in allowed_types:
            raise ValueError(f"session_type must be one of {allowed_types}")
        return v


class TrainingSessionUpdate(BaseModel):
    """Schema for updating a training session"""
    title: Optional[str] = None
    description: Optional[str] = None
    session_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    status: Optional[str] = None
    objectives: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None
    coach_name: Optional[str] = None
    coach_notes: Optional[str] = None
    intensity_level: Optional[int] = None
    effort_rating: Optional[int] = None
    fatigue_level: Optional[int] = None
    session_notes: Optional[str] = None
    player_feedback: Optional[str] = None

    @validator("intensity_level", "effort_rating", "fatigue_level")
    def validate_ratings(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Rating must be between 1 and 10")
        return v


class TrainingSessionResponse(TrainingSessionCreate):
    """Schema for training session response"""
    id: str
    duration_minutes: Optional[int] = None
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    coach_notes: Optional[str] = None
    intensity_level: Optional[int] = None
    effort_rating: Optional[int] = None
    fatigue_level: Optional[int] = None
    video_file_path: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
    session_notes: Optional[str] = None
    player_feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    drills: List[TrainingDrillResponse] = []

    class Config:
        from_attributes = True