"""
Match database model
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class MatchStatus(str, Enum):
    """Match status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class MatchType(str, Enum):
    """Match type enumeration"""
    SINGLES = "singles"
    DOUBLES = "doubles"


class Surface(str, Enum):
    """Court surface enumeration"""
    CLAY = "clay"
    GRASS = "grass"
    HARD = "hard"
    CARPET = "carpet"


class Match(Base):
    """Match model"""
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Match details
    title = Column(String(200), nullable=False)
    match_type = Column(String(20), nullable=False, default=MatchType.SINGLES)
    surface = Column(String(20), nullable=True)
    tournament_name = Column(String(200), nullable=True)
    round_name = Column(String(50), nullable=True)  # "Final", "Semi-Final", etc.

    # Players
    player1_id = Column(String, ForeignKey("players.id"), nullable=False)
    player2_id = Column(String, ForeignKey("players.id"), nullable=False)

    # Match settings
    best_of_sets = Column(Integer, default=3)  # 3 or 5 sets
    tiebreak_at = Column(Integer, default=6)  # games to trigger tiebreak

    # Score
    player1_sets = Column(Integer, default=0)
    player2_sets = Column(Integer, default=0)
    current_set = Column(Integer, default=1)

    # Status and timing
    status = Column(String(20), nullable=False, default=MatchStatus.SCHEDULED)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Video and analysis
    video_file_path = Column(String(500), nullable=True)
    analysis_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    analysis_progress = Column(Integer, default=0)  # 0-100
    analysis_data = Column(JSON, nullable=True)

    # Location
    venue = Column(String(200), nullable=True)
    court_number = Column(String(10), nullable=True)

    # Weather conditions
    weather_conditions = Column(JSON, nullable=True)

    # Additional metadata
    notes = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    player1 = relationship(
        "Player",
        foreign_keys=[player1_id],
        back_populates="matches_as_player1"
    )

    player2 = relationship(
        "Player",
        foreign_keys=[player2_id],
        back_populates="matches_as_player2"
    )

    sets = relationship(
        "Set",
        back_populates="match",
        cascade="all, delete-orphan"
    )

    points = relationship(
        "Point",
        back_populates="match",
        cascade="all, delete-orphan"
    )

    events = relationship(
        "Event",
        back_populates="match",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Match(id={self.id}, title={self.title}, status={self.status})>"