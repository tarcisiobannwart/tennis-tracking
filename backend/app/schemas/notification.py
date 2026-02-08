"""
Schemas Pydantic para notificacoes.

Implementado para TT-137: Sistema de notificacoes.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.sql.notification import NotificationType


class NotificationBase(BaseModel):
    """Base schema para notificacao."""
    notification_type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    sender_id: Optional[UUID] = None
    reference_id: Optional[UUID] = None
    reference_type: Optional[str] = None


class NotificationCreate(NotificationBase):
    """Schema para criar uma notificacao."""
    user_id: UUID


class NotificationResponse(NotificationBase):
    """Schema de resposta de notificacao."""
    id: UUID
    user_id: UUID
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema de resposta de lista de notificacoes com paginacao."""
    data: list[NotificationResponse]
    total: int
    offset: int
    limit: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """Schema de resposta de contador de nao-lidas."""
    unread_count: int
