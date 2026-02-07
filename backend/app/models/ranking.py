"""
Ranking database models for tournament rankings system
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class RankingType(str, Enum):
    """Ranking type enumeration"""
    ROUND_ROBIN = "round_robin"  # Todos contra todos
    CHALLENGE = "challenge"  # Sistema de desafio/pontos


class RankingStatus(str, Enum):
    """Ranking status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class Ranking(Base):
    """Ranking model for local/club rankings"""
    __tablename__ = "rankings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    ranking_type = Column(String(20), nullable=False, default=RankingType.ROUND_ROBIN)
    status = Column(String(20), nullable=False, default=RankingStatus.ACTIVE)

    # Location/Organization
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    venue = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)

    # Scoring configuration
    scoring_config = Column(JSON, nullable=False, default={
        "win_points": 3,
        "draw_points": 1,
        "loss_points": 0,
        "bonus_straight_sets": 1,
        "bonus_tiebreak": 0.5
    })

    # Dates
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    # Current state
    current_round = Column(Integer, default=1)
    total_rounds = Column(Integer, nullable=True)

    # Settings
    is_public = Column(Boolean, default=True)
    allow_self_scheduling = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship(
        "RankingParticipant",
        back_populates="ranking",
        cascade="all, delete-orphan"
    )
    rounds = relationship(
        "RankingRound",
        back_populates="ranking",
        cascade="all, delete-orphan",
        order_by="RankingRound.round_number"
    )
    matches = relationship(
        "RankingMatch",
        back_populates="ranking",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ranking(id={self.id}, name={self.name}, type={self.ranking_type})>"


class RankingParticipant(Base):
    """Participant in a ranking"""
    __tablename__ = "ranking_participants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    ranking_id = Column(String, ForeignKey("rankings.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Stats
    position = Column(Integer, nullable=True)
    previous_position = Column(Integer, nullable=True)
    points = Column(Float, default=0.0)
    matches_played = Column(Integer, default=0)
    matches_won = Column(Integer, default=0)
    matches_lost = Column(Integer, default=0)
    matches_drawn = Column(Integer, default=0)
    sets_won = Column(Integer, default=0)
    sets_lost = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)

    # Historical data for sparkline (array of positions over time)
    position_history = Column(JSON, default=[])

    # Status
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ranking = relationship("Ranking", back_populates="participants")
    user = relationship("User")

    def __repr__(self):
        return f"<RankingParticipant(ranking_id={self.ranking_id}, user_id={self.user_id}, position={self.position})>"


class RankingRound(Base):
    """Round in a ranking tournament"""
    __tablename__ = "ranking_rounds"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    ranking_id = Column(String, ForeignKey("rankings.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=True)  # "Round 1", "Quarterfinals", etc

    # Dates
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_completed = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ranking = relationship("Ranking", back_populates="rounds")
    matches = relationship(
        "RankingMatch",
        back_populates="round",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<RankingRound(ranking_id={self.ranking_id}, round_number={self.round_number})>"


class RankingMatch(Base):
    """Match in a ranking"""
    __tablename__ = "ranking_matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    ranking_id = Column(String, ForeignKey("rankings.id"), nullable=False)
    round_id = Column(String, ForeignKey("ranking_rounds.id"), nullable=True)

    # Match reference (links to actual match)
    match_id = Column(String, ForeignKey("matches.id"), nullable=True)

    # Players
    player1_id = Column(String, ForeignKey("users.id"), nullable=False)
    player2_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Score
    player1_score = Column(String(50), nullable=True)  # "6-4, 7-5"
    player2_score = Column(String(50), nullable=True)
    winner_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Points awarded
    player1_points = Column(Float, default=0.0)
    player2_points = Column(Float, default=0.0)

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ranking = relationship("Ranking", back_populates="matches")
    round = relationship("RankingRound", back_populates="matches")
    match = relationship("Match")
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])
    winner = relationship("User", foreign_keys=[winner_id])

    def __repr__(self):
        return f"<RankingMatch(id={self.id}, ranking_id={self.ranking_id}, status={self.status})>"
