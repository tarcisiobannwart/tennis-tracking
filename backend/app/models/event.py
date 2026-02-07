"""
Game Events SQLAlchemy model (2.0 style).

Tabela: game_events - eventos de partida em tempo real.
Usa PostgreSQL Enum para event_type e JSONB para event_data.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as PgEnum,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ============================================================
# Enums
# ============================================================

class EventType(str, Enum):
    """Tipos de evento de partida."""
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


# ============================================================
# SQLAlchemy ORM Model (2.0 style com mapped_column)
# ============================================================

class GameEvent(Base):
    """Tabela game_events - rastreamento de todos os eventos de partida."""

    __tablename__ = "game_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    match_id: Mapped[str] = mapped_column(
        String, ForeignKey("matches.id"), nullable=False
    )
    point_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("points.id"), nullable=True
    )

    # Detalhes do evento
    event_type: Mapped[str] = mapped_column(
        PgEnum(EventType, name="event_type", create_type=True),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    video_timestamp: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Segundos desde o inicio do video"
    )

    # Jogador envolvido (se aplicavel)
    player_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("players.id"), nullable=True
    )

    # Dados do evento como JSONB (flexivel para diferentes tipos)
    event_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Coordenadas na quadra (se aplicavel)
    court_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    court_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadados adicionais
    confidence: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Score de confianca do modelo AI/ML"
    )
    manual_entry: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Entrada manual vs automatizada"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    match = relationship("Match", back_populates="events")
    point = relationship("Point", back_populates="events")

    __table_args__ = (
        Index("ix_game_events_match_id", "match_id"),
        Index("ix_game_events_event_type", "event_type"),
        Index("ix_game_events_player_id", "player_id"),
        Index("ix_game_events_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<GameEvent(id={self.id}, type={self.event_type}, timestamp={self.timestamp})>"


# Alias para compatibilidade retroativa com imports existentes
# (services que usam `from app.models.event import Event`)
Event = GameEvent
