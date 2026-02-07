"""
Activity log service
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql.activity_log import ActivityLog


class ActivityLogService:
    """Service for logging user activity"""

    async def log(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        log_entry = ActivityLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(log_entry)
        await db.flush()

    async def get_user_logs(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
    ) -> tuple[list[ActivityLog], int]:
        query = select(ActivityLog).where(ActivityLog.user_id == user_id)

        if action:
            query = query.where(ActivityLog.action == action)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginated results
        query = query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()

        return list(logs), total

    async def get_all_logs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[ActivityLog], int]:
        query = select(ActivityLog)

        if action:
            query = query.where(ActivityLog.action == action)
        if user_id:
            query = query.where(ActivityLog.user_id == user_id)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginated results
        query = query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()

        return list(logs), total


activity_log_service = ActivityLogService()
