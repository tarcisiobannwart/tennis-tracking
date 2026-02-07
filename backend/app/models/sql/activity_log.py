"""
SQLAlchemy ORM model for activity_logs table.

Migrado de MongoDB/Pydantic (app.models.activity_log) para SQLAlchemy 2.0 style.
O modelo Pydantic original (ActivityLog) permanece como schema.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ActivityLog(Base):
    """
    Modelo SQLAlchemy para tabela activity_logs.

    Registra acoes dos usuarios (login, logout, upload, delete, etc.).
    FK para users.
    Campo details armazenado como JSONB para manter flexibilidade.
    """

    __tablename__ = "activity_logs"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key para user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Dados da atividade
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Request info
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="activity_logs",
    )

    # Indices equivalentes ao MongoDB
    __table_args__ = (
        Index("ix_activity_logs_user_action", "user_id", "action"),
        Index("ix_activity_logs_resource", "resource", "resource_id"),
        Index("ix_activity_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<ActivityLog(id={self.id}, user_id={self.user_id}, "
            f"action={self.action}, resource={self.resource})>"
        )
