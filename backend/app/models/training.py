"""
Training database models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class DrillDifficulty(str, Enum):
    """Drill difficulty enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class SessionStatus(str, Enum):
    """Training session status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DrillType(Base):
    """Drill type model"""
    __tablename__ = "drill_types"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # "technique", "fitness", "tactical", etc.
    difficulty = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    equipment_needed = Column(JSON, nullable=True)
    instructions = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training_drills = relationship("TrainingDrill", back_populates="drill_type")

    def __repr__(self):
        return f"<DrillType(id={self.id}, name={self.name}, category={self.category})>"


class TrainingSession(Base):
    """Training session model"""
    __tablename__ = "training_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String, ForeignKey("players.id"), nullable=False)

    # Session details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    session_type = Column(String(50), nullable=False)  # "practice", "match_prep", "recovery", etc.

    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default=SessionStatus.PLANNED)

    # Goals and objectives
    objectives = Column(JSON, nullable=True)
    focus_areas = Column(JSON, nullable=True)  # ["forehand", "serve", "footwork"]

    # Coach information
    coach_name = Column(String(100), nullable=True)
    coach_notes = Column(Text, nullable=True)

    # Performance metrics
    intensity_level = Column(Integer, nullable=True)  # 1-10 scale
    effort_rating = Column(Integer, nullable=True)  # 1-10 scale
    fatigue_level = Column(Integer, nullable=True)  # 1-10 scale

    # Video and analysis
    video_file_path = Column(String(500), nullable=True)
    analysis_data = Column(JSON, nullable=True)

    # Notes and feedback
    session_notes = Column(Text, nullable=True)
    player_feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    player = relationship("Player", back_populates="training_sessions")
    drills = relationship(
        "TrainingDrill",
        back_populates="training_session",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TrainingSession(id={self.id}, title={self.title}, status={self.status})>"


class TrainingDrill(Base):
    """Individual drill within a training session"""
    __tablename__ = "training_drills"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    training_session_id = Column(String, ForeignKey("training_sessions.id"), nullable=False)
    drill_type_id = Column(String, ForeignKey("drill_types.id"), nullable=False)

    # Drill execution
    order_in_session = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    repetitions = Column(Integer, nullable=True)
    sets = Column(Integer, nullable=True)

    # Performance metrics
    success_rate = Column(Float, nullable=True)  # 0-100%
    average_speed = Column(Float, nullable=True)
    max_speed = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)  # 0-100%

    # Drill specific data
    drill_data = Column(JSON, nullable=True)  # Custom metrics per drill type

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    coach_feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training_session = relationship("TrainingSession", back_populates="drills")
    drill_type = relationship("DrillType", back_populates="training_drills")

    def __repr__(self):
        return f"<TrainingDrill(id={self.id}, session_id={self.training_session_id})>"