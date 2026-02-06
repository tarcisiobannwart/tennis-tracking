"""
FastAPI dependencies for plan limits and feature gating
"""
from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_active_user
from app.models.user import UserInDB
from app.models.subscription import PLAN_LIMITS


def get_plan_limits(user: UserInDB) -> dict:
    """Get plan limits for current user"""
    plan = "rally"
    if user.subscription:
        plan = user.subscription.plan if isinstance(user.subscription.plan, str) else user.subscription.plan.value
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["rally"])


def require_plan(required_plans: list[str]):
    """Dependency to require specific subscription plans"""
    async def plan_checker(current_user: UserInDB = Depends(get_current_active_user)):
        user_plan = "rally"
        if current_user.subscription:
            user_plan = current_user.subscription.plan
            if not isinstance(user_plan, str):
                user_plan = user_plan.value

        if user_plan not in required_plans:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Este recurso requer um dos planos: {', '.join(required_plans)}. Seu plano atual: {user_plan}"
            )
        return current_user
    return plan_checker


def require_feature(feature: str):
    """Dependency to check if user's plan supports a feature"""
    async def feature_checker(current_user: UserInDB = Depends(get_current_active_user)):
        limits = get_plan_limits(current_user)

        if feature == "api_access" and not limits.get("api_access"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso API requer plano Grand Slam"
            )

        return current_user
    return feature_checker


# Convenience dependencies
require_paid_plan = require_plan(["match_point", "grand_slam"])
require_grand_slam = require_plan(["grand_slam"])
