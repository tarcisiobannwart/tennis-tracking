"""
Modelos SQLAlchemy para analysis_tasks e analysis_results.

Migrado de MongoDB/Pydantic (backend/app/models/analysis.py) para SQLAlchemy 2.0 style.
Os modelos Pydantic originais sao mantidos como schemas (AnalysisTask, AnalysisResult, etc.).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
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

if TYPE_CHECKING:
    from app.models.sql.video import Video


class AnalysisStatusEnum(str, enum.Enum):
    """Status de uma tarefa de analise."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisTask(Base):
    """
    Modelo SQLAlchemy para tabela analysis_tasks.

    Representa uma tarefa de analise de video (rastreamento de bola,
    deteccao de quadra, deteccao de jogadores, etc.).
    Equivalente a collection 'analysis_tasks' do MongoDB.
    """

    __tablename__ = "analysis_tasks"
    __table_args__ = (
        Index("ix_analysis_tasks_video_id", "video_id"),
        Index("ix_analysis_tasks_user_id", "user_id"),
        Index("ix_analysis_tasks_status", "status"),
        Index("ix_analysis_tasks_created_at", "created_at"),
    )

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    match_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AnalysisStatusEnum.PENDING.value,
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSONB fields
    config: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # Detection results (JSONB - dados estruturados grandes)
    ball_detections: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    player_detections: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    court_detection: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    shot_detections: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    rallies: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Statistics
    total_frames: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_frames: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    detection_accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Match and player statistics (JSONB)
    match_stats: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    player_stats_data: Mapped[dict | None] = mapped_column(
        "player_stats_data",
        JSONB,
        nullable=True,
    )

    # Highlights
    highlights: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Processing metadata
    processing_time: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    model_versions: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
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

    # Relationships
    video: Mapped[Video] = relationship(
        "Video",
        back_populates="analysis_tasks",
    )

    def __repr__(self) -> str:
        return f"<AnalysisTask(id={self.id}, video_id={self.video_id}, status={self.status})>"
