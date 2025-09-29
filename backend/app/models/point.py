"""
Point database model
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class ShotType(str, Enum):
    """Shot type enumeration"""
    SERVE = "serve"
    FOREHAND = "forehand"
    BACKHAND = "backhand"
    VOLLEY = "volley"
    SMASH = "smash"
    LOB = "lob"
    DROP_SHOT = "drop_shot"
    RETURN = "return"


class PointOutcome(str, Enum):
    """Point outcome enumeration"""
    WINNER = "winner"
    UNFORCED_ERROR = "unforced_error"
    FORCED_ERROR = "forced_error"
    ACE = "ace"
    DOUBLE_FAULT = "double_fault"
    LET = "let"


class Point(Base):
    """Point model"""
    __tablename__ = "points"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    set_id = Column(String, ForeignKey("sets.id"), nullable=False)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)

    # Point details
    point_number = Column(Integer, nullable=False)
    server_player_id = Column(String, ForeignKey("players.id"), nullable=False)
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    # Score before this point
    score_before = Column(JSON, nullable=True)  # {"player1": "30", "player2": "15"}

    # Point outcome
    outcome = Column(String(20), nullable=True)
    winning_shot = Column(String(20), nullable=True)

    # Rally information
    rally_length = Column(Integer, default=0)  # Number of shots in rally
    rally_duration = Column(Float, nullable=True)  # Duration in seconds

    # Serve information
    serve_speed = Column(Float, nullable=True)  # km/h or mph
    serve_placement = Column(JSON, nullable=True)  # Court coordinates
    first_serve_in = Column(Boolean, nullable=True)
    second_serve = Column(Boolean, default=False)

    # Ball tracking data
    ball_trajectory = Column(JSON, nullable=True)  # Array of coordinates over time
    bounce_points = Column(JSON, nullable=True)  # Ball bounce coordinates

    # Player positions
    player_positions = Column(JSON, nullable=True)  # Player movement during rally

    # Video timestamps
    video_start_time = Column(Float, nullable=True)  # Seconds from start of video
    video_end_time = Column(Float, nullable=True)

    # Analysis data
    analysis_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    match = relationship("Match", back_populates="points")
    set = relationship("Set")
    game = relationship("Game", back_populates="points")
    events = relationship(
        "Event",
        back_populates="point",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Point(id={self.id}, point_number={self.point_number}, outcome={self.outcome})>"