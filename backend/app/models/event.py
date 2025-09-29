"""
Event database model for real-time match events
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class EventType(str, Enum):
    """Event type enumeration"""
    POINT_STARTED = "point_started"
    POINT_SCORED = "point_scored"
    GAME_WON = "game_won"
    SET_WON = "set_won"
    MATCH_WON = "match_won"
    SERVE = "serve"
    SHOT = "shot"
    BALL_BOUNCE = "ball_bounce"
    PLAYER_POSITION = "player_position"
    COURT_DETECTION = "court_detection"
    ERROR = "error"
    LET = "let"
    CHALLENGE = "challenge"


class Event(Base):
    """Event model for tracking all match events"""
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    point_id = Column(String, ForeignKey("points.id"), nullable=True)

    # Event details
    event_type = Column(String(30), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    video_timestamp = Column(Float, nullable=True)  # Seconds from video start

    # Player involved (if applicable)
    player_id = Column(String, ForeignKey("players.id"), nullable=True)

    # Event data
    event_data = Column(JSON, nullable=True)

    # Court coordinates (if applicable)
    court_x = Column(Float, nullable=True)
    court_y = Column(Float, nullable=True)

    # Additional metadata
    confidence = Column(Float, nullable=True)  # AI/ML confidence score
    manual_entry = Column(Boolean, default=False)  # Human vs automated entry

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    match = relationship("Match", back_populates="events")
    point = relationship("Point", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, timestamp={self.timestamp})>"