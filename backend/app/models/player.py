"""
Player database model
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Player(Base):
    """Player model"""
    __tablename__ = "players"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    age = Column(Integer, nullable=True)
    country = Column(String(3), nullable=True)  # ISO country code

    # Physical attributes
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    dominant_hand = Column(String(10), nullable=True)  # "right", "left", "ambidextrous"

    # Tennis specific
    ranking = Column(Integer, nullable=True)
    skill_level = Column(String(20), nullable=True)  # "beginner", "intermediate", "advanced", "professional"

    # Profile
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    matches_as_player1 = relationship(
        "Match",
        foreign_keys="[Match.player1_id]",
        back_populates="player1"
    )

    matches_as_player2 = relationship(
        "Match",
        foreign_keys="[Match.player2_id]",
        back_populates="player2"
    )

    training_sessions = relationship(
        "TrainingSession",
        back_populates="player"
    )

    def __repr__(self):
        return f"<Player(id={self.id}, name={self.name})>"