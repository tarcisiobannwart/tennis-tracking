"""
Modelo SQLAlchemy para videos.

Migrado de MongoDB/Pydantic (backend/app/models/video.py) para SQLAlchemy 2.0 style.
Os modelos Pydantic originais sao mantidos como schemas (VideoCreate, VideoResponse).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.sql.analysis import AnalysisTask


class VideoStatusEnum(str, enum.Enum):
    """Status do processamento de video."""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(Base):
    """
    Modelo SQLAlchemy para tabela videos.

    Representa um video de partida de tenis enviado para analise.
    Equivalente a collection 'videos' do MongoDB.
    """

    __tablename__ = "videos"
    __table_args__ = (
        Index("ix_videos_user_id", "user_id"),
        Index("ix_videos_status", "status"),
        Index("ix_videos_match_id", "match_id"),
        Index("ix_videos_uploaded_at", "uploaded_at"),
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

    # File info
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Video metadata
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Paths
    upload_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    processed_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    thumbnail_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=VideoStatusEnum.UPLOADING.value,
    )
    processing_progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSONB fields (metadata e analysis_results do MongoDB)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )
    analysis_results: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # Relationships
    analysis_tasks: Mapped[list[AnalysisTask]] = relationship(
        "AnalysisTask",
        back_populates="video",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, filename={self.filename}, status={self.status})>"
