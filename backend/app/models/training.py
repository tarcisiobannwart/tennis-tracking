"""
Training MongoDB models (Pydantic)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DrillDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class SessionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SessionType(str, Enum):
    PRACTICE = "practice"
    MATCH_PREP = "match_prep"
    RECOVERY = "recovery"
    FITNESS = "fitness"
    TECHNIQUE = "technique"
    TACTICAL = "tactical"


class DrillCategory(str, Enum):
    TECHNIQUE = "technique"
    FITNESS = "fitness"
    TACTICAL = "tactical"
    SERVE = "serve"
    RETURN = "return"
    VOLLEY = "volley"
    FOOTWORK = "footwork"
    MENTAL = "mental"


# --- DrillType ---

class DrillTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    difficulty: str
    duration_minutes: Optional[int] = None
    equipment_needed: Optional[List[str]] = None
    instructions: Optional[str] = None


class DrillTypeCreate(DrillTypeBase):
    pass


class DrillTypeInDB(DrillTypeBase):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class DrillTypeResponse(DrillTypeBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# --- TrainingDrill ---

class TrainingDrillBase(BaseModel):
    drill_type_id: str
    drill_name: Optional[str] = None
    order_in_session: int = 0
    duration_minutes: Optional[int] = None
    repetitions: Optional[int] = None
    sets: Optional[int] = None


class TrainingDrillCreate(TrainingDrillBase):
    pass


class TrainingDrillInDB(TrainingDrillBase):
    id: Optional[str] = None
    success_rate: Optional[float] = None
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None
    accuracy_score: Optional[float] = None
    drill_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    notes: Optional[str] = None
    coach_feedback: Optional[str] = None


class TrainingDrillResponse(TrainingDrillBase):
    id: Optional[str] = None
    success_rate: Optional[float] = None
    accuracy_score: Optional[float] = None
    drill_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    notes: Optional[str] = None


# --- TrainingSession ---

class TrainingSessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    session_type: str = "practice"
    scheduled_at: datetime
    objectives: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None
    coach_name: Optional[str] = None


class TrainingSessionCreate(TrainingSessionBase):
    pass


class TrainingSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    session_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
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


class TrainingSessionInDB(TrainingSessionBase):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    status: str = SessionStatus.PLANNED.value
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    coach_notes: Optional[str] = None
    intensity_level: Optional[int] = None
    effort_rating: Optional[int] = None
    fatigue_level: Optional[int] = None
    video_file_path: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
    session_notes: Optional[str] = None
    player_feedback: Optional[str] = None
    drills: List[TrainingDrillInDB] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class TrainingSessionResponse(TrainingSessionBase):
    id: str
    user_id: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    coach_notes: Optional[str] = None
    intensity_level: Optional[int] = None
    effort_rating: Optional[int] = None
    fatigue_level: Optional[int] = None
    session_notes: Optional[str] = None
    player_feedback: Optional[str] = None
    drills: List[TrainingDrillResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
