"""
Subscription service - Stripe integration
"""
import logging
from typing import Optional
from datetime import datetime

from app.core.config import settings
from app.core.mongodb import get_collection
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
        user_id: str,
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

        users = get_collection("users")
        user = await users.find_one({"_id": user_id})

        # Get or create Stripe customer
        customer_id = None
        if user and user.get("subscription", {}).get("stripeCustomerId"):
            customer_id = user["subscription"]["stripeCustomerId"]
        else:
            customer = self.stripe.Customer.create(
                email=user_email,
                metadata={"user_id": user_id},
            )
            customer_id = customer.id
            await users.update_one(
                {"_id": user_id},
                {"$set": {"subscription.stripeCustomerId": customer_id}}
            )

        plan_info = PLAN_LIMITS.get(plan, {})
        trial_days = plan_info.get("trial_days")

        session_params = {
            "customer": customer_id,
            "payment_method_types": ["card"],
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": f"{settings.FRONTEND_URL}/app/settings?tab=subscription&status=success",
            "cancel_url": f"{settings.FRONTEND_URL}/app/settings?tab=subscription&status=cancelled",
            "metadata": {"user_id": user_id, "plan": plan},
        }

        if trial_days:
            session_params["subscription_data"] = {
                "trial_period_days": trial_days,
            }

        session = self.stripe.checkout.Session.create(**session_params)
        return session.url

    async def create_portal_session(self, user_id: str) -> Optional[str]:
        """Create Stripe customer portal session, return URL"""
        if not self.stripe:
            return None

        users = get_collection("users")
        user = await users.find_one({"_id": user_id})

        customer_id = None
        if user and user.get("subscription", {}).get("stripeCustomerId"):
            customer_id = user["subscription"]["stripeCustomerId"]

        if not customer_id:
            return None

        session = self.stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.FRONTEND_URL}/app/settings?tab=subscription",
        )
        return session.url

    async def handle_webhook_event(self, event: dict) -> bool:
        """Process Stripe webhook event"""
        event_type = event.get("type", "")
        data = event.get("data", {}).get("object", {})

        # Log event
        sub_events = get_collection("subscription_events")
        await sub_events.insert_one({
            "stripeEventId": event.get("id"),
            "eventType": event_type,
            "data": data,
            "processed": False,
            "createdAt": datetime.utcnow(),
        })

        users = get_collection("users")

        if event_type == "checkout.session.completed":
            user_id = data.get("metadata", {}).get("user_id")
            plan = data.get("metadata", {}).get("plan")
            subscription_id = data.get("subscription")

            if user_id and plan:
                await users.update_one(
                    {"_id": user_id},
                    {"$set": {
                        "subscription.plan": plan,
                        "subscription.status": "active",
                        "subscription.stripeSubscriptionId": subscription_id,
                        "updatedAt": datetime.utcnow(),
                    }}
                )

        elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
            subscription_id = data.get("id")
            status_val = data.get("status")
            cancel_at_period_end = data.get("cancel_at_period_end", False)
            current_period_start = data.get("current_period_start")
            current_period_end = data.get("current_period_end")
            trial_end = data.get("trial_end")

            user = await users.find_one({"subscription.stripeSubscriptionId": subscription_id})
            if user:
                update = {
                    "subscription.status": status_val,
                    "subscription.cancelAtPeriodEnd": cancel_at_period_end,
                    "updatedAt": datetime.utcnow(),
                }
                if current_period_start:
                    update["subscription.currentPeriodStart"] = datetime.fromtimestamp(current_period_start)
                if current_period_end:
                    update["subscription.currentPeriodEnd"] = datetime.fromtimestamp(current_period_end)
                if trial_end:
                    update["subscription.trialEnd"] = datetime.fromtimestamp(trial_end)

                await users.update_one({"_id": user["_id"]}, {"$set": update})

        elif event_type == "customer.subscription.deleted":
            subscription_id = data.get("id")
            user = await users.find_one({"subscription.stripeSubscriptionId": subscription_id})
            if user:
                await users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {
                        "subscription.plan": "rally",
                        "subscription.status": "canceled",
                        "subscription.stripeSubscriptionId": None,
                        "subscription.cancelAtPeriodEnd": False,
                        "updatedAt": datetime.utcnow(),
                    }}
                )

        elif event_type == "invoice.payment_failed":
            subscription_id = data.get("subscription")
            user = await users.find_one({"subscription.stripeSubscriptionId": subscription_id})
            if user:
                await users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {
                        "subscription.status": "past_due",
                        "updatedAt": datetime.utcnow(),
                    }}
                )

        # Mark event as processed
        await sub_events.update_one(
            {"stripeEventId": event.get("id")},
            {"$set": {"processed": True}}
        )

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
