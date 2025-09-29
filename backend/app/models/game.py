"""
Game database model
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Game(Base):
    """Game model"""
    __tablename__ = "games"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    set_id = Column(String, ForeignKey("sets.id"), nullable=False)
    game_number = Column(Integer, nullable=False)

    # Score
    player1_score = Column(String(10), default="0")  # "0", "15", "30", "40", "AD"
    player2_score = Column(String(10), default="0")

    # Server
    server_player_id = Column(String, ForeignKey("players.id"), nullable=False)

    # Status
    is_completed = Column(Boolean, default=False)
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    # Deuce tracking
    deuce_count = Column(Integer, default=0)
    advantage_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Statistics
    game_stats = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    match = relationship("Match")
    set = relationship("Set", back_populates="games")
    points = relationship(
        "Point",
        back_populates="game",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Game(id={self.id}, game_number={self.game_number}, score={self.player1_score}-{self.player2_score})>"