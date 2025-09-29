"""
Set database model
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Set(Base):
    """Set model"""
    __tablename__ = "sets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    set_number = Column(Integer, nullable=False)

    # Score
    player1_games = Column(Integer, default=0)
    player2_games = Column(Integer, default=0)

    # Tiebreak scores (if applicable)
    player1_tiebreak = Column(Integer, nullable=True)
    player2_tiebreak = Column(Integer, nullable=True)
    is_tiebreak = Column(Boolean, default=False)

    # Status
    is_completed = Column(Boolean, default=False)
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Statistics
    set_stats = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    match = relationship("Match", back_populates="sets")
    games = relationship(
        "Game",
        back_populates="set",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Set(id={self.id}, match_id={self.match_id}, set_number={self.set_number})>"