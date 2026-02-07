"""
Admin service - metrics, user management
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql.user import User
from app.models.sql.video import Video
from app.models.sql.subscription_event import SubscriptionEvent


class AdminService:
    """Service for admin operations"""

    async def get_dashboard_metrics(self, db: AsyncSession) -> dict:
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total users
        total_users_result = await db.execute(select(func.count()).select_from(User))
        total_users = total_users_result.scalar() or 0

        # New users this month
        new_users_result = await db.execute(
            select(func.count()).select_from(User).where(User.created_at >= first_of_month)
        )
        new_users_month = new_users_result.scalar() or 0

        # Active users
        active_users_result = await db.execute(
            select(func.count()).select_from(User).where(User.is_active == True)
        )
        active_users = active_users_result.scalar() or 0

        # Total videos
        total_videos_result = await db.execute(select(func.count()).select_from(Video))
        total_videos = total_videos_result.scalar() or 0

        # Subscription breakdown
        rally_result = await db.execute(
            select(func.count()).select_from(User).where(User.subscription["plan"].astext == "rally")
        )
        rally_count = rally_result.scalar() or 0

        match_point_result = await db.execute(
            select(func.count()).select_from(User).where(User.subscription["plan"].astext == "match_point")
        )
        match_point_count = match_point_result.scalar() or 0

        grand_slam_result = await db.execute(
            select(func.count()).select_from(User).where(User.subscription["plan"].astext == "grand_slam")
        )
        grand_slam_count = grand_slam_result.scalar() or 0

        # MRR calculation
        mrr = (match_point_count * 9700 + grand_slam_count * 29700) / 100  # em reais

        # Role breakdown
        admin_result = await db.execute(
            select(func.count()).select_from(User).where(User.role == "admin")
        )
        admin_count = admin_result.scalar() or 0

        coach_result = await db.execute(
            select(func.count()).select_from(User).where(User.role == "coach")
        )
        coach_count = coach_result.scalar() or 0

        player_result = await db.execute(
            select(func.count()).select_from(User).where(User.role == "player")
        )
        player_count = player_result.scalar() or 0

        return {
            "totalUsers": total_users,
            "newUsersThisMonth": new_users_month,
            "activeUsers": active_users,
            "totalVideos": total_videos,
            "mrr": mrr,
            "subscriptions": {
                "rally": rally_count,
                "match_point": match_point_count,
                "grand_slam": grand_slam_count,
            },
            "roles": {
                "admin": admin_count,
                "coach": coach_count,
                "player": player_count,
            },
        }

    async def update_user_role(self, db: AsyncSession, user_id: uuid.UUID, role: str) -> bool:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.role = role
        await db.flush()
        return True

    async def update_user_plan(self, db: AsyncSession, user_id: uuid.UUID, plan: str) -> bool:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        if not user.subscription:
            user.subscription = {}
        user.subscription["plan"] = plan
        user.subscription["status"] = "active"
        await db.flush()
        return True

    async def toggle_user_active(self, db: AsyncSession, user_id: uuid.UUID, is_active: bool) -> bool:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.is_active = is_active
        await db.flush()
        return True

    async def get_subscription_stats(self, db: AsyncSession) -> dict:
        # Plan breakdown using JSONB query
        plan_counts = {}
        for plan in ["rally", "match_point", "grand_slam"]:
            result = await db.execute(
                select(func.count()).select_from(User).where(User.subscription["plan"].astext == plan)
            )
            plan_counts[plan] = result.scalar() or 0

        # Recent events
        result = await db.execute(
            select(SubscriptionEvent)
            .order_by(SubscriptionEvent.created_at.desc())
            .limit(20)
        )
        recent_events = result.scalars().all()

        return {
            "planBreakdown": plan_counts,
            "recentEvents": [
                {
                    "id": str(event.id),
                    "user_id": str(event.user_id),
                    "stripe_event_id": event.stripe_event_id,
                    "event_type": event.event_type,
                    "data": event.data,
                    "processed": event.processed,
                    "created_at": event.created_at.isoformat(),
                }
                for event in recent_events
            ],
        }


admin_service = AdminService()
