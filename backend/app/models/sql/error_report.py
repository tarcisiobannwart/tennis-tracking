"""
SQLAlchemy ORM model for error_reports table.

Armazena erros capturados automaticamente (frontend e backend)
com fingerprint para deduplicacao e referencia ao Jira issue.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ErrorSourceEnum(str, PyEnum):
    """Origem do erro"""
    frontend = "frontend"
    backend = "backend"


class ErrorReportStatusEnum(str, PyEnum):
    """Status do error report"""
    open = "open"
    reported = "reported"
    resolved = "resolved"
    ignored = "ignored"


class ErrorReport(Base):
    """
    Modelo SQLAlchemy para tabela error_reports.

    Cada registro representa um erro unico identificado por fingerprint.
    Erros duplicados incrementam occurrence_count e adicionam comentario no Jira.
    """

    __tablename__ = "error_reports"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Fingerprint SHA256 para deduplicacao
    fingerprint: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    # Origem: frontend ou backend
    source: Mapped[str] = mapped_column(
        ENUM('frontend', 'backend', name='error_source_enum', create_type=False),
        nullable=False,
        index=True,
    )

    # Tipo do erro (ex: TypeError, ValueError, NetworkError)
    error_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # Mensagem do erro
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Stack trace completo
    stack_trace: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Jira issue key (ex: TT-150)
    jira_issue_key: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    # Contagem de ocorrencias (incrementa em duplicatas)
    occurrence_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # Status do report
    status: Mapped[str] = mapped_column(
        ENUM('open', 'reported', 'resolved', 'ignored', name='error_report_status_enum', create_type=False),
        default='open',
        nullable=False,
        index=True,
    )

    # Contexto adicional (URL, method, user_agent, user_id, etc.)
    context: Mapped[dict | None] = mapped_column(
        JSONB,
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
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Indices compostos
    __table_args__ = (
        Index("ix_error_reports_source_status", "source", "status"),
        Index("ix_error_reports_created_at", "created_at"),
        Index("ix_error_reports_last_seen_at", "last_seen_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<ErrorReport(id={self.id}, fingerprint={self.fingerprint[:12]}..., "
            f"error_type={self.error_type}, count={self.occurrence_count})>"
        )
