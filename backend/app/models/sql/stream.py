"""
Modelo SQLAlchemy para streams.

Migrado de MongoDB/Pydantic (backend/app/models/stream.py) para SQLAlchemy 2.0 style.
Os modelos Pydantic originais sao mantidos como schemas (StreamCreate, StreamResponse).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class StreamStatusEnum(str, enum.Enum):
    """Status de um stream de camera ao vivo."""
    WAITING = "waiting"
    LIVE = "live"
    ENDED = "ended"


class Stream(Base):
    """
    Modelo SQLAlchemy para tabela streams.

    Representa um stream de camera ao vivo para transmissao de partidas.
    Equivalente a collection 'streams' do MongoDB.
    """

    __tablename__ = "streams"
    __table_args__ = (
        Index("ix_streams_user_id", "user_id"),
        Index("ix_streams_status", "status"),
        Index("ix_streams_stream_key", "stream_key", unique=True),
        Index("ix_streams_match_id", "match_id"),
        Index("ix_streams_created_at", "created_at"),
    )

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    match_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Stream identification
    stream_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    camera_label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Camera 1",
    )

    # URLs
    rtmp_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    hls_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    rtsp_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=StreamStatusEnum.WAITING.value,
    )
    is_recording: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    viewer_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # JSONB fields
    device_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {"platform": "unknown"},
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
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
        return f"<Stream(id={self.id}, stream_key={self.stream_key}, status={self.status})>"
