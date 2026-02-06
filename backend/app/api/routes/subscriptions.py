"""
Subscriptions API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.core.auth import get_current_active_user
from app.core.config import settings
from app.models.user import UserInDB
from app.services.subscription_service import subscription_service

router = APIRouter(tags=["subscriptions"])


class CheckoutRequest(BaseModel):
    plan: str


@router.get("/plans")
async def get_plans():
    """Get available subscription plans"""
    return subscription_service.get_plans()


@router.post("/checkout")
async def create_checkout(
    data: CheckoutRequest,
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Create Stripe checkout session"""
    if data.plan not in ("match_point", "grand_slam"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plano invalido"
        )

    url = await subscription_service.create_checkout_session(
        user_id=str(current_user.id),
        user_email=current_user.email,
        plan=data.plan,
    )

    if not url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servico de pagamento indisponivel"
        )

    return {"url": url}


@router.post("/portal")
async def create_portal(
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Create Stripe customer portal session"""
    url = await subscription_service.create_portal_session(str(current_user.id))

    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma assinatura ativa encontrada"
        )

    return {"url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        # Dev mode - parse raw JSON
        import json
        event = json.loads(payload)
    else:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    await subscription_service.handle_webhook_event(event)
    return {"status": "ok"}
