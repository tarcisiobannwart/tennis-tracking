"""
User service - CRUD, password management, profile
"""
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_password_hash, verify_password
from app.models.sql.user import User, SubscriptionPlan, SubscriptionStatus
from app.models.sql.video import Video
from app.models.user import UserCreate, UserUpdate, UserSubscription


class UserService:
    """Service for user management"""

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user_data: UserCreate) -> User:
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.fullName,
            password=get_password_hash(user_data.password),
            role=user_data.role if hasattr(user_data, 'role') else "viewer",
            is_active=True,
            email_verified=False,
            subscription={
                "plan": SubscriptionPlan.RALLY.value,
                "status": SubscriptionStatus.ACTIVE.value,
                "stripe_customer_id": None,
                "stripe_subscription_id": None,
                "current_period_start": None,
                "current_period_end": None,
                "cancel_at_period_end": False,
                "trial_end": None,
            },
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, user_id: uuid.UUID, update_data: dict) -> Optional[User]:
        user = await self.get_by_id(db, user_id)
        if not user:
            return None

        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await db.flush()
        await db.refresh(user)
        return user

    async def change_password(self, db: AsyncSession, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        user = await self.get_by_id(db, user_id)
        if not user:
            return False
        if not verify_password(current_password, user.password):
            return False

        user.password = get_password_hash(new_password)
        await db.flush()
        return True

    async def create_password_reset_token(self, db: AsyncSession, email: str) -> Optional[str]:
        user = await self.get_by_email(db, email)
        if not user:
            return None

        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        await db.flush()
        return token

    async def reset_password(self, db: AsyncSession, token: str, new_password: str) -> bool:
        result = await db.execute(
            select(User).where(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.utcnow()
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        await db.flush()
        return True

    async def create_email_verification_token(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[str]:
        user = await self.get_by_id(db, user_id)
        if not user:
            return None

        token = secrets.token_urlsafe(32)
        user.email_verification_token = token
        await db.flush()
        return token

    async def verify_email(self, db: AsyncSession, token: str) -> bool:
        result = await db.execute(
            select(User).where(User.email_verification_token == token)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.email_verified = True
        user.email_verification_token = None
        await db.flush()
        return True

    async def get_by_username_or_email(self, db: AsyncSession, identifier: str) -> Optional[User]:
        result = await db.execute(
            select(User).where(
                or_(User.username == identifier, User.email == identifier)
            )
        )
        return result.scalar_one_or_none()

    async def update_refresh_token(self, db: AsyncSession, user_id: uuid.UUID, token: Optional[str]) -> bool:
        user = await self.get_by_id(db, user_id)
        if not user:
            return False
        user.refresh_token = token
        await db.flush()
        return True

    async def update_last_login(self, db: AsyncSession, user_id: uuid.UUID) -> bool:
        user = await self.get_by_id(db, user_id)
        if not user:
            return False
        user.last_login = datetime.utcnow()
        await db.flush()
        return True

    async def update_subscription(self, db: AsyncSession, user_id: uuid.UUID, subscription: dict) -> Optional[User]:
        user = await self.get_by_id(db, user_id)
        if not user:
            return None

        user.subscription = subscription
        await db.flush()
        await db.refresh(user)
        return user

    async def get_video_count_this_month(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        result = await db.execute(
            select(func.count()).select_from(Video).where(
                Video.user_id == user_id,
                Video.uploaded_at >= first_of_month
            )
        )
        return result.scalar() or 0

    async def list_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        plan: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[list[User], int]:
        query = select(User)

        if role:
            query = query.where(User.role == role)
        if plan:
            # JSONB query para subscription.plan
            query = query.where(User.subscription["plan"].astext == plan)
        if search:
            query = query.where(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginated results
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()

        return list(users), total


user_service = UserService()
