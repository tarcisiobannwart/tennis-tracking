"""
Training SQLAlchemy models + Pydantic schemas.

Tabelas: drill_types, training_sessions
Drills armazenados como JSONB array dentro de training_sessions.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    DateTime,
    Enum as PgEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ============================================================
# Enums (compartilhados entre SQLAlchemy e Pydantic)
# ============================================================

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


# ============================================================
# SQLAlchemy ORM Models (2.0 style com mapped_column)
# ============================================================

class DrillType(Base):
    """Tabela drill_types - catalogo de exercicios de treino."""

    __tablename__ = "drill_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        PgEnum(DrillCategory, name="drill_category", create_type=True),
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        PgEnum(DrillDifficulty, name="drill_difficulty", create_type=True),
        nullable=False,
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    equipment_needed: Mapped[Optional[list]] = mapped_column(
        ARRAY(String), nullable=True
    )
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    __table_args__ = (
        Index("ix_drill_types_category", "category"),
        Index("ix_drill_types_difficulty", "difficulty"),
        Index("ix_drill_types_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<DrillType(id={self.id}, name={self.name}, category={self.category})>"


class TrainingSession(Base):
    """Tabela training_sessions - sessoes de treino com drills como JSONB."""

    __tablename__ = "training_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento com player (usuario)
    player_id: Mapped[str] = mapped_column(
        String, ForeignKey("players.id"), nullable=False
    )

    # Dados da sessao
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_type: Mapped[str] = mapped_column(
        PgEnum(SessionType, name="session_type", create_type=True),
        nullable=False,
        default=SessionType.PRACTICE,
    )
    status: Mapped[str] = mapped_column(
        PgEnum(SessionStatus, name="session_status", create_type=True),
        nullable=False,
        default=SessionStatus.PLANNED,
    )

    # Agendamento e duracao
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Objetivos e foco (arrays de texto)
    objectives: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    focus_areas: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)

    # Coach
    coach_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    coach_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metricas de esforco
    intensity_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    effort_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fatigue_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Video e analise
    video_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    analysis_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Notas e feedback
    session_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    player_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Drills como JSONB array (cada drill contem drill_type_id, metricas, etc.)
    drills: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    player = relationship("Player", back_populates="training_sessions")

    __table_args__ = (
        Index("ix_training_sessions_player_id", "player_id"),
        Index("ix_training_sessions_status", "status"),
        Index("ix_training_sessions_session_type", "session_type"),
        Index("ix_training_sessions_scheduled_at", "scheduled_at"),
    )

    def __repr__(self) -> str:
        return f"<TrainingSession(id={self.id}, title={self.title}, status={self.status})>"


# ============================================================
# Pydantic Schemas (mantidos para validacao de request/response)
# ============================================================

# --- DrillType Schemas ---

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
    id: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class DrillTypeResponse(DrillTypeBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# --- TrainingDrill Schemas ---

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


# --- TrainingSession Schemas ---

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
    id: Optional[str] = Field(None)
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
