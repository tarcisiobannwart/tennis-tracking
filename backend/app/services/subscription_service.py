"""
Subscription service - Stripe integration
"""
import logging
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.sql.user import User
from app.models.sql.subscription_event import SubscriptionEvent
from app.models.subscription import PLAN_LIMITS

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing subscriptions via Stripe"""

    def __init__(self):
        self._stripe = None

    @property
    def stripe(self):
        if self._stripe is None and settings.STRIPE_SECRET_KEY:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                self._stripe = stripe
            except ImportError:
                logger.warning("stripe package not installed")
        return self._stripe

    def get_price_id(self, plan: str) -> Optional[str]:
        """Get Stripe price ID for a plan"""
        price_map = {
            "match_point": settings.STRIPE_PRICE_MATCH_POINT_MONTHLY,
            "grand_slam": settings.STRIPE_PRICE_GRAND_SLAM_MONTHLY,
        }
        return price_map.get(plan)

    async def create_checkout_session(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        user_email: str,
        plan: str,
    ) -> Optional[str]:
        """Create Stripe checkout session, return URL"""
        if not self.stripe:
            logger.warning("Stripe not configured")
            return None

        price_id = self.get_price_id(plan)
        if not price_id:
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        # Get or create Stripe customer
        customer_id = None
        if user.subscription and user.subscription.get("stripe_customer_id"):
            customer_id = user.subscription["stripe_customer_id"]
        else:
            customer = self.stripe.Customer.create(
                email=user_email,
                metadata={"user_id": str(user_id)},
            )
            customer_id = customer.id
            if not user.subscription:
                user.subscription = {}
            user.subscription["stripe_customer_id"] = customer_id
            await db.flush()

        plan_info = PLAN_LIMITS.get(plan, {})
        trial_days = plan_info.get("trial_days")

        session_params = {
            "customer": customer_id,
            "payment_method_types": ["card"],
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": f"{settings.FRONTEND_URL}/app/settings?tab=subscription&status=success",
            "cancel_url": f"{settings.FRONTEND_URL}/app/settings?tab=subscription&status=cancelled",
            "metadata": {"user_id": str(user_id), "plan": plan},
        }

        if trial_days:
            session_params["subscription_data"] = {
                "trial_period_days": trial_days,
            }

        session = self.stripe.checkout.Session.create(**session_params)
        return session.url

    async def create_portal_session(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[str]:
        """Create Stripe customer portal session, return URL"""
        if not self.stripe:
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        customer_id = None
        if user.subscription and user.subscription.get("stripe_customer_id"):
            customer_id = user.subscription["stripe_customer_id"]

        if not customer_id:
            return None

        session = self.stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.FRONTEND_URL}/app/settings?tab=subscription",
        )
        return session.url

    async def handle_webhook_event(self, db: AsyncSession, event: dict) -> bool:
        """Process Stripe webhook event"""
        event_type = event.get("type", "")
        data = event.get("data", {}).get("object", {})

        # Note: We need user_id to create SubscriptionEvent with FK
        # For now, we'll try to extract user_id from metadata or subscription lookup
        user_id_str = data.get("metadata", {}).get("user_id")
        if not user_id_str:
            # Try to find user by stripe_subscription_id
            subscription_id = data.get("id") if event_type.startswith("customer.subscription") else data.get("subscription")
            if subscription_id:
                user_result = await db.execute(
                    select(User).where(User.subscription["stripe_subscription_id"].astext == subscription_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user_id_str = str(user.id)

        if user_id_str:
            try:
                user_id = uuid.UUID(user_id_str)
                # Log event
                event_log = SubscriptionEvent(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    stripe_event_id=event.get("id"),
                    event_type=event_type,
                    data=data,
                    processed=False,
                )
                db.add(event_log)
                await db.flush()
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id for subscription event: {user_id_str}")

        if event_type == "checkout.session.completed":
            user_id_meta = data.get("metadata", {}).get("user_id")
            plan = data.get("metadata", {}).get("plan")
            subscription_id = data.get("subscription")

            if user_id_meta and plan:
                try:
                    user_uuid = uuid.UUID(user_id_meta)
                    user_result = await db.execute(select(User).where(User.id == user_uuid))
                    user = user_result.scalar_one_or_none()
                    if user:
                        if not user.subscription:
                            user.subscription = {}
                        user.subscription["plan"] = plan
                        user.subscription["status"] = "active"
                        user.subscription["stripe_subscription_id"] = subscription_id
                        await db.flush()
                except ValueError:
                    pass

        elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
            subscription_id = data.get("id")
            status_val = data.get("status")
            cancel_at_period_end = data.get("cancel_at_period_end", False)
            current_period_start = data.get("current_period_start")
            current_period_end = data.get("current_period_end")
            trial_end = data.get("trial_end")

            user_result = await db.execute(
                select(User).where(User.subscription["stripe_subscription_id"].astext == subscription_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                if not user.subscription:
                    user.subscription = {}
                user.subscription["status"] = status_val
                user.subscription["cancel_at_period_end"] = cancel_at_period_end
                if current_period_start:
                    user.subscription["current_period_start"] = datetime.fromtimestamp(current_period_start).isoformat()
                if current_period_end:
                    user.subscription["current_period_end"] = datetime.fromtimestamp(current_period_end).isoformat()
                if trial_end:
                    user.subscription["trial_end"] = datetime.fromtimestamp(trial_end).isoformat()
                await db.flush()

        elif event_type == "customer.subscription.deleted":
            subscription_id = data.get("id")
            user_result = await db.execute(
                select(User).where(User.subscription["stripe_subscription_id"].astext == subscription_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                if not user.subscription:
                    user.subscription = {}
                user.subscription["plan"] = "rally"
                user.subscription["status"] = "canceled"
                user.subscription["stripe_subscription_id"] = None
                user.subscription["cancel_at_period_end"] = False
                await db.flush()

        elif event_type == "invoice.payment_failed":
            subscription_id = data.get("subscription")
            user_result = await db.execute(
                select(User).where(User.subscription["stripe_subscription_id"].astext == subscription_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                if not user.subscription:
                    user.subscription = {}
                user.subscription["status"] = "past_due"
                await db.flush()

        # Mark event as processed
        if user_id_str:
            try:
                await db.execute(
                    select(SubscriptionEvent).where(SubscriptionEvent.stripe_event_id == event.get("id"))
                )
                # Update processed flag
                event_result = await db.execute(
                    select(SubscriptionEvent).where(SubscriptionEvent.stripe_event_id == event.get("id"))
                )
                event_obj = event_result.scalar_one_or_none()
                if event_obj:
                    event_obj.processed = True
                    await db.flush()
            except Exception as e:
                logger.warning(f"Failed to mark event as processed: {e}")

        return True

    def get_plans(self) -> list[dict]:
        """Get available subscription plans"""
        plans = []
        for plan_id, info in PLAN_LIMITS.items():
            plans.append({
                "id": plan_id,
                "name": info["name"],
                "price": info["price"],
                "currency": "brl",
                "interval": "month",
                "features": {
                    "videos_per_month": info["videos_per_month"],
                    "max_video_duration": info["max_video_duration"],
                    "models": info["models"],
                    "history_days": info["history_days"],
                    "max_team_members": info["max_team_members"],
                    "api_access": info["api_access"],
                },
            })
        return plans


subscription_service = SubscriptionService()
