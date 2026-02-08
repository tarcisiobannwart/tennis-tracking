"""
Notification Service - gerenciamento de notificacoes.

Implementado para TT-137: Sistema de notificacoes com feed cronologico,
contador de nao-lidas e push notifications via WebSocket.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.sql.notification import Notification, NotificationType
from app.schemas.notification import NotificationCreate
from app.api.websocket.live_stream import send_notification_to_user

logger = structlog.get_logger(__name__)


class NotificationService:
    """Servico para gerenciamento de notificacoes."""

    @staticmethod
    async def list_notifications(
        db: AsyncSession,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int, int]:
        """
        Lista notificacoes de um usuario com paginacao.

        Args:
            db: Sessao do banco de dados
            user_id: ID do usuario
            offset: Offset para paginacao
            limit: Limite de itens por pagina

        Returns:
            Tupla com (lista de notificacoes, total de notificacoes, total de nao-lidas)
        """
        try:
            # Query para total de notificacoes
            total_query = select(func.count(Notification.id)).where(
                Notification.user_id == user_id
            )
            total_result = await db.execute(total_query)
            total = total_result.scalar() or 0

            # Query para total de nao-lidas
            unread_query = select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            unread_result = await db.execute(unread_query)
            unread_count = unread_result.scalar() or 0

            # Query para notificacoes com paginacao
            query = (
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            result = await db.execute(query)
            notifications = result.scalars().all()

            logger.info(
                "Notificacoes listadas",
                user_id=str(user_id),
                total=total,
                unread=unread_count,
                returned=len(notifications),
            )

            return list(notifications), total, unread_count

        except Exception as e:
            logger.error("Erro ao listar notificacoes", error=str(e), user_id=str(user_id))
            raise

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:
        """
        Obtem contador de notificacoes nao-lidas.

        Args:
            db: Sessao do banco de dados
            user_id: ID do usuario

        Returns:
            Total de notificacoes nao-lidas
        """
        try:
            query = select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            result = await db.execute(query)
            count = result.scalar() or 0

            logger.info("Contador de nao-lidas", user_id=str(user_id), count=count)
            return count

        except Exception as e:
            logger.error("Erro ao obter contador de nao-lidas", error=str(e), user_id=str(user_id))
            raise

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Notification]:
        """
        Marca uma notificacao como lida.

        Args:
            db: Sessao do banco de dados
            notification_id: ID da notificacao
            user_id: ID do usuario (para validacao de propriedade)

        Returns:
            Notificacao atualizada ou None se nao encontrada
        """
        try:
            # Verificar se notificacao existe e pertence ao usuario
            query = select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            result = await db.execute(query)
            notification = result.scalar_one_or_none()

            if not notification:
                logger.warning(
                    "Notificacao nao encontrada",
                    notification_id=str(notification_id),
                    user_id=str(user_id),
                )
                return None

            # Marcar como lida
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await db.commit()
            await db.refresh(notification)

            logger.info(
                "Notificacao marcada como lida",
                notification_id=str(notification_id),
                user_id=str(user_id),
            )

            return notification

        except Exception as e:
            logger.error(
                "Erro ao marcar notificacao como lida",
                error=str(e),
                notification_id=str(notification_id),
                user_id=str(user_id),
            )
            await db.rollback()
            raise

    @staticmethod
    async def mark_all_as_read(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:
        """
        Marca todas as notificacoes de um usuario como lidas.

        Args:
            db: Sessao do banco de dados
            user_id: ID do usuario

        Returns:
            Numero de notificacoes atualizadas
        """
        try:
            query = (
                update(Notification)
                .where(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
                .values(
                    is_read=True,
                    read_at=datetime.utcnow(),
                )
            )
            result = await db.execute(query)
            await db.commit()

            updated_count = result.rowcount

            logger.info(
                "Todas as notificacoes marcadas como lidas",
                user_id=str(user_id),
                count=updated_count,
            )

            return updated_count

        except Exception as e:
            logger.error(
                "Erro ao marcar todas as notificacoes como lidas",
                error=str(e),
                user_id=str(user_id),
            )
            await db.rollback()
            raise

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        notification_data: NotificationCreate,
    ) -> Notification:
        """
        Cria uma nova notificacao.

        Args:
            db: Sessao do banco de dados
            notification_data: Dados da notificacao

        Returns:
            Notificacao criada
        """
        try:
            notification = Notification(
                user_id=notification_data.user_id,
                notification_type=notification_data.notification_type,
                title=notification_data.title,
                message=notification_data.message,
                sender_id=notification_data.sender_id,
                reference_id=notification_data.reference_id,
                reference_type=notification_data.reference_type,
            )

            db.add(notification)
            await db.commit()
            await db.refresh(notification)

            logger.info(
                "Notificacao criada",
                notification_id=str(notification.id),
                user_id=str(notification_data.user_id),
                type=notification_data.notification_type,
            )

            # Enviar notificacao via WebSocket (nao-bloqueante)
            try:
                await send_notification_to_user(
                    user_id=str(notification_data.user_id),
                    notification_data={
                        "id": str(notification.id),
                        "notification_type": notification.notification_type,
                        "title": notification.title,
                        "message": notification.message,
                        "sender_id": str(notification.sender_id) if notification.sender_id else None,
                        "reference_id": str(notification.reference_id) if notification.reference_id else None,
                        "reference_type": notification.reference_type,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    }
                )
            except Exception as e:
                # Nao falhar se WebSocket nao estiver disponivel
                logger.warning("Erro ao enviar notificacao via WebSocket", error=str(e))

            return notification

        except Exception as e:
            logger.error(
                "Erro ao criar notificacao",
                error=str(e),
                user_id=str(notification_data.user_id),
            )
            await db.rollback()
            raise

    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Deleta uma notificacao.

        Args:
            db: Sessao do banco de dados
            notification_id: ID da notificacao
            user_id: ID do usuario (para validacao de propriedade)

        Returns:
            True se deletada com sucesso, False se nao encontrada
        """
        try:
            query = delete(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            result = await db.execute(query)
            await db.commit()

            deleted = result.rowcount > 0

            if deleted:
                logger.info(
                    "Notificacao deletada",
                    notification_id=str(notification_id),
                    user_id=str(user_id),
                )
            else:
                logger.warning(
                    "Notificacao nao encontrada para deletar",
                    notification_id=str(notification_id),
                    user_id=str(user_id),
                )

            return deleted

        except Exception as e:
            logger.error(
                "Erro ao deletar notificacao",
                error=str(e),
                notification_id=str(notification_id),
                user_id=str(user_id),
            )
            await db.rollback()
            raise
