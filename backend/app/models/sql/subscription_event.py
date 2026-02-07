"""
SQLAlchemy ORM model for subscription_events table.

Migrado de MongoDB/Pydantic (app.models.subscription) para SQLAlchemy 2.0 style.
Os modelos Pydantic originais (SubscriptionEvent, PlanInfo, etc.) permanecem como schemas.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubscriptionEvent(Base):
    """
    Modelo SQLAlchemy para tabela subscription_events.

    Armazena eventos do Stripe webhook.
    FK para users.
    Campo data armazenado como JSONB para manter payload flexivel.
    """

    __tablename__ = "subscription_events"

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

    # Dados do evento Stripe
    stripe_event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    data: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="subscription_events",
    )

    # Indices
    __table_args__ = (
        Index("ix_sub_events_user_type", "user_id", "event_type"),
        Index("ix_sub_events_processed", "processed"),
    )

    def __repr__(self) -> str:
        return (
            f"<SubscriptionEvent(id={self.id}, stripe_event_id={self.stripe_event_id}, "
            f"event_type={self.event_type})>"
        )
