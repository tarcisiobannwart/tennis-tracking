"""
SQLAlchemy ORM models para tournaments, tournament_categories e tournament_registrations.

Tabelas:
- tournaments: Dados principais do torneio
- tournament_categories: Categorias dentro de um torneio (ex: Masculino A, Feminino B)
- tournament_registrations: Inscricoes de jogadores nos torneios
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ============================================================
# Enums
# ============================================================

class TournamentStatus(str, Enum):
    """Status do torneio"""
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentType(str, Enum):
    """Tipo de torneio"""
    SINGLES = "singles"
    DOUBLES = "doubles"
    MIXED = "mixed"
    TEAM = "team"


class RegistrationStatus(str, Enum):
    """Status da inscricao"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLIST = "waitlist"


class PaymentStatus(str, Enum):
    """Status do pagamento"""
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


# ============================================================
# SQLAlchemy ORM Models
# ============================================================

class Tournament(Base):
    """Tabela tournaments - dados principais dos torneios."""

    __tablename__ = "tournaments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Dados basicos
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sport: Mapped[str] = mapped_column(String(50), nullable=False, default="tennis")
    tournament_type: Mapped[str] = mapped_column(
        ENUM('singles', 'doubles', 'mixed', 'team', name='tournament_type', create_type=False),
        nullable=False,
        default='singles',
    )
    status: Mapped[str] = mapped_column(
        ENUM('draft', 'open', 'closed', 'in_progress', 'completed', 'cancelled', name='tournament_status', create_type=False),
        nullable=False,
        default='draft',
    )

    # Organizador (usuario ou organizacao)
    organizer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )

    # Local
    venue_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    venue_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    venue_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Brazil")

    # Datas
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Inscricoes
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_participants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    registration_fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")

    # Configuracoes
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_waitlist: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    require_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Metadados adicionais (regras, premios, etc.)
    rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prizes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    contact_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    additional_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Imagens
    banner_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    organizer = relationship("User", foreign_keys=[organizer_id])
    organization = relationship("Organization", foreign_keys=[organization_id])
    categories = relationship("TournamentCategory", back_populates="tournament", cascade="all, delete-orphan")
    registrations = relationship("TournamentRegistration", back_populates="tournament", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tournaments_status", "status"),
        Index("ix_tournaments_sport", "sport"),
        Index("ix_tournaments_organizer_id", "organizer_id"),
        Index("ix_tournaments_organization_id", "organization_id"),
        Index("ix_tournaments_start_date", "start_date"),
        Index("ix_tournaments_state", "state"),
        Index("ix_tournaments_city", "city"),
    )

    def __repr__(self) -> str:
        return f"<Tournament(id={self.id}, name={self.name}, status={self.status})>"


class TournamentCategory(Base):
    """Tabela tournament_categories - categorias dentro de um torneio."""

    __tablename__ = "tournament_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento com torneio
    tournament_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=False
    )

    # Dados da categoria
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Restricoes
    min_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    skill_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Limites
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_participants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Taxa especifica da categoria (sobrescreve a do torneio)
    registration_fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    tournament = relationship("Tournament", back_populates="categories")
    registrations = relationship("TournamentRegistration", back_populates="category")

    __table_args__ = (
        Index("ix_tournament_categories_tournament_id", "tournament_id"),
        Index("ix_tournament_categories_gender", "gender"),
        Index("ix_tournament_categories_skill_level", "skill_level"),
    )

    def __repr__(self) -> str:
        return f"<TournamentCategory(id={self.id}, name={self.name})>"


class TournamentRegistration(Base):
    """Tabela tournament_registrations - inscricoes de jogadores."""

    __tablename__ = "tournament_registrations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamentos
    tournament_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tournament_categories.id"), nullable=False
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Dados adicionais do jogador (capturados no momento da inscricao)
    player_name: Mapped[str] = mapped_column(String(200), nullable=False)
    player_email: Mapped[str] = mapped_column(String(255), nullable=False)
    player_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    player_document: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Para doubles/team
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    partner_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    team_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        ENUM('pending', 'confirmed', 'cancelled', 'waitlist', name='registration_status', create_type=False),
        nullable=False,
        default='pending',
    )

    # Pagamento
    payment_status: Mapped[str] = mapped_column(
        ENUM('pending', 'paid', 'refunded', 'failed', name='payment_status', create_type=False),
        nullable=False,
        default='pending',
    )
    amount_paid: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metadados adicionais
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    medical_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    tournament = relationship("Tournament", back_populates="registrations")
    category = relationship("TournamentCategory", back_populates="registrations")
    player = relationship("User", foreign_keys=[player_id])
    partner = relationship("User", foreign_keys=[partner_id])

    __table_args__ = (
        Index("ix_tournament_registrations_tournament_id", "tournament_id"),
        Index("ix_tournament_registrations_category_id", "category_id"),
        Index("ix_tournament_registrations_player_id", "player_id"),
        Index("ix_tournament_registrations_status", "status"),
        Index("ix_tournament_registrations_payment_status", "payment_status"),
    )

    def __repr__(self) -> str:
        return f"<TournamentRegistration(id={self.id}, player_name={self.player_name}, status={self.status})>"
