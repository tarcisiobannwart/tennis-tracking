"""
Point History SQLAlchemy model + Pydantic schemas.

Tabela: point_history - historico detalhado de cada ponto jogado.
Usa PostgreSQL Enum para outcome e JSONB para dados de posicao/trajetoria.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as PgEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ============================================================
# Enums
# ============================================================

class PointOutcome(str, Enum):
    """Tipos de resultado de ponto."""
    ACE = "ace"
    WINNER = "winner"
    UNFORCED_ERROR = "unforced_error"
    FORCED_ERROR = "forced_error"
    DOUBLE_FAULT = "double_fault"
    SERVICE_WINNER = "service_winner"
    RETURN_WINNER = "return_winner"
    VOLLEY_WINNER = "volley_winner"
    SMASH_WINNER = "smash_winner"
    DROP_SHOT_WINNER = "drop_shot_winner"
    LET = "let"
    NET = "net"
    OUT = "out"
    LONG = "long"
    WIDE = "wide"


# ============================================================
# SQLAlchemy ORM Model (2.0 style com mapped_column)
# ============================================================

class PointHistory(Base):
    """Tabela point_history - historico detalhado de pontos com 15+ campos."""

    __tablename__ = "point_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Identificadores
    match_id: Mapped[str] = mapped_column(
        String, ForeignKey("matches.id"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    game_number: Mapped[int] = mapped_column(Integer, nullable=False)
    point_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Contexto de placar (JSONB para flexibilidade)
    score_before: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="Placar antes do ponto (e.g., {'player1': '30', 'player2': '15'})"
    )
    score_after: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="Placar apos o ponto"
    )
    set_score_before: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="Placar de games no set antes do ponto"
    )
    set_score_after: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="Placar de games no set apos o ponto"
    )

    # Jogadores
    server_player_id: Mapped[str] = mapped_column(
        String, ForeignKey("players.id"), nullable=False
    )
    receiver_player_id: Mapped[str] = mapped_column(
        String, ForeignKey("players.id"), nullable=False
    )
    point_winner_id: Mapped[str] = mapped_column(
        String, ForeignKey("players.id"), nullable=False
    )

    # Resultado do ponto
    outcome: Mapped[str] = mapped_column(
        PgEnum(PointOutcome, name="point_outcome", create_type=True),
        nullable=False,
    )
    winning_shot: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Informacao do rally
    rally_length: Mapped[int] = mapped_column(Integer, default=0)
    rally_duration: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Duracao do rally em segundos"
    )

    # Informacao do saque
    is_first_serve: Mapped[bool] = mapped_column(Boolean, default=True)
    serve_speed: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Velocidade do saque em km/h"
    )
    serve_placement: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="Posicao do saque (wide, body, T)"
    )
    is_serve_in: Mapped[bool] = mapped_column(Boolean, default=True)

    # Contexto estrategico
    is_break_point: Mapped[bool] = mapped_column(Boolean, default=False)
    is_set_point: Mapped[bool] = mapped_column(Boolean, default=False)
    is_match_point: Mapped[bool] = mapped_column(Boolean, default=False)
    is_game_point: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timing
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    video_timestamp: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Timestamp no video em segundos"
    )

    # Dados adicionais (JSONB)
    court_position_data: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Posicoes dos jogadores durante o ponto"
    )
    ball_trajectory_data: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Dados de trajetoria da bola"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps de auditoria
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    match = relationship("Match")
    server_player = relationship("Player", foreign_keys=[server_player_id])
    receiver_player = relationship("Player", foreign_keys=[receiver_player_id])
    point_winner = relationship("Player", foreign_keys=[point_winner_id])

    __table_args__ = (
        Index("ix_point_history_match_id", "match_id"),
        Index("ix_point_history_outcome", "outcome"),
        Index("ix_point_history_server_player_id", "server_player_id"),
        Index("ix_point_history_point_winner_id", "point_winner_id"),
        Index("ix_point_history_match_set_game", "match_id", "set_number", "game_number"),
        Index("ix_point_history_break_point", "is_break_point"),
    )

    def __repr__(self) -> str:
        return (
            f"<PointHistory(id={self.id}, match={self.match_id}, "
            f"set={self.set_number}, game={self.game_number}, point={self.point_number})>"
        )


# ============================================================
# Pydantic Schemas (mantidos para validacao de request/response)
# ============================================================

class PointDetails(BaseModel):
    """
    Informacao detalhada sobre um unico ponto.
    Contem 15+ campos para analise abrangente.
    """
    # Identificadores
    point_id: str = Field(..., description="Unique point ID")
    match_id: str = Field(..., description="Match ID")
    set_number: int = Field(..., description="Set number (1-5)")
    game_number: int = Field(..., description="Game number in set")
    point_number: int = Field(..., description="Point number in game")

    # Contexto de placar
    score_before: Dict[str, str] = Field(
        ..., description="Score before point (e.g., {'player1': '30', 'player2': '15'})"
    )
    score_after: Dict[str, str] = Field(..., description="Score after point")
    set_score_before: Dict[str, int] = Field(
        ..., description="Set score before point (games)"
    )
    set_score_after: Dict[str, int] = Field(
        ..., description="Set score after point (games)"
    )

    # Jogadores
    server_player_id: str = Field(..., description="Server player ID")
    receiver_player_id: str = Field(..., description="Receiver player ID")
    point_winner_id: str = Field(..., description="Point winner player ID")

    # Resultado do ponto
    outcome: PointOutcome = Field(..., description="How the point ended")
    winning_shot: Optional[str] = Field(None, description="Type of winning shot")
    error_type: Optional[str] = Field(None, description="Type of error if applicable")

    # Rally
    rally_length: int = Field(default=0, description="Number of shots in rally")
    rally_duration: Optional[float] = Field(None, description="Rally duration in seconds")

    # Saque
    is_first_serve: bool = Field(default=True, description="Whether this was a first serve")
    serve_speed: Optional[float] = Field(None, description="Serve speed in km/h")
    serve_placement: Optional[str] = Field(
        None, description="Serve placement (wide, body, T)"
    )
    is_serve_in: bool = Field(default=True, description="Whether serve was in")

    # Contexto estrategico
    is_break_point: bool = Field(default=False, description="Whether this was a break point")
    is_set_point: bool = Field(default=False, description="Whether this was a set point")
    is_match_point: bool = Field(default=False, description="Whether this was a match point")
    is_game_point: bool = Field(default=False, description="Whether this was a game point")

    # Timing
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When point occurred"
    )
    video_timestamp: Optional[float] = Field(
        None, description="Video timestamp in seconds"
    )

    # Dados adicionais
    court_position_data: Optional[Dict[str, Any]] = Field(
        None, description="Player positions during point"
    )
    ball_trajectory_data: Optional[Dict[str, Any]] = Field(
        None, description="Ball trajectory data"
    )
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        use_enum_values = True


class PointHistoryFilter(BaseModel):
    """Filtro para consulta de historico de pontos."""
    match_id: Optional[str] = None
    player_id: Optional[str] = None
    set_number: Optional[int] = None
    outcome: Optional[PointOutcome] = None
    is_break_point: Optional[bool] = None
    is_set_point: Optional[bool] = None
    is_match_point: Optional[bool] = None
    min_rally_length: Optional[int] = None
    max_rally_length: Optional[int] = None


class PointHistorySummary(BaseModel):
    """Estatisticas resumidas do historico de pontos."""
    total_points: int
    points_by_outcome: Dict[str, int]
    average_rally_length: float
    break_points_total: int
    break_points_converted: int
    aces_count: int
    double_faults_count: int
    winners_count: int
    unforced_errors_count: int
