"""
Notifications API routes.

Implementado para TT-137: Sistema de notificacoes com feed cronologico,
contador de nao-lidas e push notifications via WebSocket.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.sql.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
)

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    offset: int = Query(0, ge=0, description="Offset para paginacao"),
    limit: int = Query(20, ge=1, le=100, description="Limite de itens por pagina"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtem lista paginada de notificacoes do usuario autenticado.

    Args:
        offset: Offset para paginacao (default: 0)
        limit: Limite de itens por pagina (1-100, default: 20)
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Lista paginada de notificacoes com contador de nao-lidas
    """
    try:
        notifications, total, unread_count = await NotificationService.list_notifications(
            db=db,
            user_id=current_user.id,
            offset=offset,
            limit=limit,
        )

        return NotificationListResponse(
            data=[NotificationResponse.from_orm(n) for n in notifications],
            total=total,
            offset=offset,
            limit=limit,
            unread_count=unread_count,
        )

    except Exception as e:
        logger.error("Erro ao listar notificacoes", error=str(e), user_id=str(current_user.id))
        raise HTTPException(status_code=500, detail="Erro ao listar notificacoes")


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtem contador de notificacoes nao-lidas do usuario autenticado.

    Args:
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Contador de notificacoes nao-lidas
    """
    try:
        unread_count = await NotificationService.get_unread_count(
            db=db,
            user_id=current_user.id,
        )

        return UnreadCountResponse(unread_count=unread_count)

    except Exception as e:
        logger.error("Erro ao obter contador de nao-lidas", error=str(e), user_id=str(current_user.id))
        raise HTTPException(status_code=500, detail="Erro ao obter contador de nao-lidas")


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: uuid.UUID = Path(..., description="ID da notificacao"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Marca uma notificacao como lida.

    Args:
        notification_id: ID da notificacao
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Notificacao atualizada
    """
    try:
        notification = await NotificationService.mark_as_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id,
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notificacao nao encontrada")

        return NotificationResponse.from_orm(notification)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Erro ao marcar notificacao como lida",
            error=str(e),
            notification_id=str(notification_id),
            user_id=str(current_user.id),
        )
        raise HTTPException(status_code=500, detail="Erro ao marcar notificacao como lida")


@router.put("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Marca todas as notificacoes do usuario como lidas.

    Args:
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Numero de notificacoes atualizadas
    """
    try:
        updated_count = await NotificationService.mark_all_as_read(
            db=db,
            user_id=current_user.id,
        )

        return {"updated_count": updated_count, "message": "Todas as notificacoes foram marcadas como lidas"}

    except Exception as e:
        logger.error(
            "Erro ao marcar todas as notificacoes como lidas",
            error=str(e),
            user_id=str(current_user.id),
        )
        raise HTTPException(status_code=500, detail="Erro ao marcar todas as notificacoes como lidas")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: uuid.UUID = Path(..., description="ID da notificacao"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deleta uma notificacao.

    Args:
        notification_id: ID da notificacao
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Mensagem de sucesso
    """
    try:
        deleted = await NotificationService.delete_notification(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id,
        )

        if not deleted:
            raise HTTPException(status_code=404, detail="Notificacao nao encontrada")

        return {"message": "Notificacao deletada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Erro ao deletar notificacao",
            error=str(e),
            notification_id=str(notification_id),
            user_id=str(current_user.id),
        )
        raise HTTPException(status_code=500, detail="Erro ao deletar notificacao")
