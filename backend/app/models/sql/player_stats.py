"""
Modelo SQLAlchemy para player_stats.

Estatisticas de jogadores por partida, calculadas a partir das analises de video.
Modelo novo criado para PostgreSQL (nao existia como modelo formal no MongoDB).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class PlayerStats(Base):
    """
    Modelo SQLAlchemy para tabela player_stats.

    Armazena estatisticas detalhadas de um jogador em uma partida especifica,
    como velocidade de saque, porcentagem de acerto, distancia percorrida, etc.
    """

    __tablename__ = "player_stats"
    __table_args__ = (
        Index("ix_player_stats_player_id", "player_id"),
        Index("ix_player_stats_match_id", "match_id"),
        Index("ix_player_stats_player_match", "player_id", "match_id", unique=True),
        Index("ix_player_stats_created_at", "created_at"),
    )

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
    )
    match_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Serve statistics
    first_serve_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    second_serve_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    aces: Mapped[int | None] = mapped_column(Integer, nullable=True)
    double_faults: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_first_serve_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_second_serve_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_serve_speed: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Rally statistics
    total_shots: Mapped[int | None] = mapped_column(Integer, nullable=True)
    forehand_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    backhand_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    volley_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    smash_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    winners: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unforced_errors: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Movement statistics
    total_distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Points statistics
    points_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    points_lost: Mapped[int | None] = mapped_column(Integer, nullable=True)
    break_points_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    break_points_total: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # JSONB for extended/custom stats
    extended_stats: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<PlayerStats(id={self.id}, player_id={self.player_id}, match_id={self.match_id})>"
