"""
SQLAlchemy ORM models for venues (locais/clubes) table.

Models para gestão de locais/clubes esportivos com suporte a
seguidores, membros associados e contadores de engajamento.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VenueMemberRole(str, PyEnum):
    """Venue member role enumeration para PostgreSQL."""
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"


class Venue(Base):
    """
    Modelo SQLAlchemy para tabela venues (locais/clubes).

    Representa locais esportivos com informações completas,
    incluindo localização, amenidades e contadores sociais.
    """

    __tablename__ = "venues"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Identificação
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(250),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Imagens
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Localização
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Contato
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Infraestrutura (JSON para flexibilidade)
    sport_types: Mapped[list | None] = mapped_column(
        JSONB,
        default=list,
        comment="['tennis', 'padel', 'squash', etc]"
    )
    court_count: Mapped[int] = mapped_column(Integer, default=0)
    surface_types: Mapped[list | None] = mapped_column(
        JSONB,
        default=list,
        comment="['clay', 'hard', 'grass', 'synthetic']"
    )
    amenities: Mapped[list | None] = mapped_column(
        JSONB,
        default=list,
        comment="['lockers', 'shower', 'restaurant', 'parking', 'pro_shop', 'coaching']"
    )

    # Contadores sociais
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    members_count: Mapped[int] = mapped_column(Integer, default=0)

    # Configurações
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)

    # Owner
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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
    members = relationship(
        "VenueMember",
        back_populates="venue",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    followers = relationship(
        "VenueFollower",
        back_populates="venue",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Indices
    __table_args__ = (
        Index("ix_venues_slug", "slug"),
        Index("ix_venues_city_country", "city", "country"),
        Index("ix_venues_is_public", "is_public"),
        Index("ix_venues_owner_id", "owner_id"),
    )

    def __repr__(self) -> str:
        return f"<Venue(id={self.id}, name={self.name}, slug={self.slug})>"


class VenueMember(Base):
    """
    Modelo SQLAlchemy para tabela venue_members.

    Representa associação de usuários a locais/clubes,
    com papéis (member, admin, owner).
    """

    __tablename__ = "venue_members"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("venues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Role
    role: Mapped[str] = mapped_column(
        Enum(VenueMemberRole, name="venue_member_role", create_constraint=True),
        nullable=False,
        default=VenueMemberRole.MEMBER,
    )

    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    venue = relationship("Venue", back_populates="members")

    # Unique constraint: user can't be member twice of same venue
    __table_args__ = (
        Index("ix_venue_members_venue_user", "venue_id", "user_id", unique=True),
        Index("ix_venue_members_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<VenueMember(venue_id={self.venue_id}, user_id={self.user_id}, role={self.role})>"


class VenueFollower(Base):
    """
    Modelo SQLAlchemy para tabela venue_followers.

    Representa seguidores de locais/clubes (follow sem associação formal).
    """

    __tablename__ = "venue_followers"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("venues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Timestamps
    followed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    venue = relationship("Venue", back_populates="followers")

    # Unique constraint: user can't follow venue twice
    __table_args__ = (
        Index("ix_venue_followers_venue_user", "venue_id", "user_id", unique=True),
        Index("ix_venue_followers_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<VenueFollower(venue_id={self.venue_id}, user_id={self.user_id})>"
