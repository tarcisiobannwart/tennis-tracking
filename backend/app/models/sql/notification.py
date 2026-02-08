"""
SQLAlchemy ORM model para notifications table.

Implementado para TT-137: Sistema de notificacoes com feed cronologico,
diferentes tipos de eventos (resultado de jogo, amizade aceita, jogo agendado, etc),
contador de nao-lidas e push notifications via WebSocket.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NotificationType(str, PyEnum):
    """Tipos de notificacao."""
    MATCH_RESULT = "match_result"
    FRIENDSHIP = "friendship"
    GAME_SCHEDULED = "game_scheduled"
    RANKING_ROUND = "ranking_round"
    TOURNAMENT = "tournament"
    SYSTEM = "system"


class Notification(Base):
    """
    Modelo SQLAlchemy para tabela notifications.

    Representa uma notificacao enviada a um usuario, que pode ser:
    - Resultado de partida (match_result)
    - Amizade aceita (friendship)
    - Jogo agendado (game_scheduled)
    - Nova rodada de ranking (ranking_round)
    - Evento de torneio (tournament)
    - Notificacao do sistema (system)
    """

    __tablename__ = "notifications"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Usuario que recebe a notificacao
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo de notificacao
    notification_type: Mapped[str] = mapped_column(
        Enum(NotificationType, name="notification_type", create_constraint=True),
        nullable=False,
        default=NotificationType.SYSTEM,
    )

    # Conteudo da notificacao
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Remetente da notificacao (opcional - pode ser sistema)
    sender_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Referencia generica para entidade relacionada
    reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Estado de leitura
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Indices para performance
    __table_args__ = (
        Index("ix_notifications_user_created", "user_id", "created_at"),
        Index("ix_notifications_user_read", "user_id", "is_read"),
        Index("ix_notifications_type", "notification_type"),
        Index("ix_notifications_reference", "reference_id", "reference_type"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.notification_type})>"
