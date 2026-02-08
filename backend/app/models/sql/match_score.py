"""
SQLAlchemy ORM model for match_scores table.

Armazena o estado completo de pontuacao de uma partida de tenis,
incluindo sets, games e pontos via campo JSONB score_data.
O modelo Pydantic MatchScore permanece como schema.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MatchScoreSQL(Base):
    """
    Modelo SQLAlchemy para tabela match_scores.

    O campo score_data armazena o estado completo de pontuacao
    como JSONB (sets, current_set, current_game, etc.).
    """

    __tablename__ = "match_scores"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Match identification
    match_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Players
    player1_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    player2_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Match format
    format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="best_of_3",
    )

    # Current server
    current_server_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Match state
    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    winner_player_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Full scoring state (sets, current_set, current_game)
    score_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<MatchScoreSQL(id={self.id}, match_id={self.match_id}, "
            f"is_complete={self.is_complete})>"
        )
