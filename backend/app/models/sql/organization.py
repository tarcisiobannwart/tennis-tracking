"""
SQLAlchemy ORM models for organizations and organization_invites tables.

Migrado de MongoDB/Pydantic (app.models.organization) para SQLAlchemy 2.0 style.
Os modelos Pydantic originais (OrganizationCreate, OrganizationResponse, etc.)
permanecem como schemas.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrganizationPlan(str, PyEnum):
    """Organization plan enumeration."""
    RALLY = "rally"
    MATCH_POINT = "match_point"
    GRAND_SLAM = "grand_slam"


class InviteStatus(str, PyEnum):
    """Invite status enumeration para PostgreSQL."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Organization(Base):
    """
    Modelo SQLAlchemy para tabela organizations.

    Campo members armazenado como JSONB array para manter flexibilidade
    da estrutura semi-estruturada original do MongoDB.
    Formato: [{"user_id": "uuid", "role": "member", "joined_at": "iso-datetime"}]
    """

    __tablename__ = "organizations"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Dados basicos
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Plano
    plan: Mapped[str] = mapped_column(
        ENUM('rally', 'match_point', 'grand_slam', name='organization_plan', create_type=False),
        nullable=False,
        default='grand_slam',
    )
    max_members: Mapped[int] = mapped_column(Integer, default=10)

    # Members (JSONB array para manter flexibilidade)
    members: Mapped[list | None] = mapped_column(
        JSONB,
        default=list,
    )

    # Stripe
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
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
    invites = relationship(
        "OrganizationInvite",
        back_populates="organization",
        lazy="selectin",
    )

    # Indices
    __table_args__ = (
        Index("ix_organizations_owner_id", "owner_id"),
        Index("ix_organizations_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"


class OrganizationInvite(Base):
    """
    Modelo SQLAlchemy para tabela organization_invites.

    Convites para membros se juntarem a organizacoes.
    FK para organizations.
    """

    __tablename__ = "organization_invites"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key para organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Dados do convite
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
    )
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Status
    status: Mapped[str] = mapped_column(
        ENUM('pending', 'accepted', 'expired', 'cancelled', name='invite_status', create_type=False),
        nullable=False,
        default='pending',
    )

    # Expiracao
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    organization = relationship(
        "Organization",
        back_populates="invites",
    )

    # Indices
    __table_args__ = (
        Index("ix_org_invites_org_status", "organization_id", "status"),
        Index("ix_org_invites_email_status", "email", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationInvite(id={self.id}, email={self.email}, "
            f"status={self.status})>"
        )
