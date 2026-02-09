"""
SQLAlchemy ORM model for users table.

Migrado de MongoDB/Pydantic (app.models.user) para SQLAlchemy 2.0 style.
Os modelos Pydantic originais (UserCreate, UserResponse, etc.) permanecem como schemas.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, PyEnum):
    """User role enumeration para PostgreSQL."""
    ADMIN = "admin"
    COACH = "coach"
    PLAYER = "player"
    ANALYST = "analyst"
    VIEWER = "viewer"


class SubscriptionPlan(str, PyEnum):
    """Subscription plan enumeration para PostgreSQL."""
    RALLY = "rally"
    MATCH_POINT = "match_point"
    GRAND_SLAM = "grand_slam"


class SubscriptionStatus(str, PyEnum):
    """Subscription status enumeration para PostgreSQL."""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"


class User(Base):
    """
    Modelo SQLAlchemy para tabela users.

    Campos subscription_* armazenados como JSONB para manter flexibilidade
    da estrutura semi-estruturada original do MongoDB.
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Dados basicos
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        ENUM('admin', 'coach', 'player', 'analyst', 'viewer', name='user_role', create_type=False),
        nullable=False,
        default='viewer',
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Perfil
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="pt-BR")
    preferences: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Perfil Social TT-129
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)  # male, female, other
    height_cm: Mapped[int | None] = mapped_column(nullable=True)
    laterality: Mapped[str | None] = mapped_column(String(20), nullable=True)  # right, left
    backhand_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # one-handed, two-handed
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Subscription (JSONB para manter flexibilidade)
    subscription: Mapped[dict | None] = mapped_column(
        JSONB,
        default=lambda: {
            "plan": SubscriptionPlan.RALLY.value,
            "status": SubscriptionStatus.ACTIVE.value,
            "stripe_customer_id": None,
            "stripe_subscription_id": None,
            "current_period_start": None,
            "current_period_end": None,
            "cancel_at_period_end": False,
            "trial_end": None,
        },
    )

    # Organization
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    organization_role: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Email verification
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Password reset
    password_reset_token: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    password_reset_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Tokens
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Auth
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
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

    # Relationships
    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        lazy="selectin",
    )
    subscription_events = relationship(
        "SubscriptionEvent",
        back_populates="user",
        lazy="selectin",
    )

    # Indices equivalentes ao MongoDB
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_role", "role"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
