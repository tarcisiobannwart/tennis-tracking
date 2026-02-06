"""
Admin API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from app.core.auth import require_admin
from app.models.user import UserInDB
from app.services.admin_service import admin_service
from app.services.user_service import user_service
from app.services.activity_log_service import activity_log_service

router = APIRouter(tags=["admin"])


class UpdateUserRoleRequest(BaseModel):
    role: str


class UpdateUserPlanRequest(BaseModel):
    plan: str


class UpdateUserActiveRequest(BaseModel):
    is_active: bool


@router.get("/metrics")
async def get_metrics(current_user: UserInDB = Depends(require_admin)):
    """Get admin dashboard metrics"""
    return await admin_service.get_dashboard_metrics()


@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    plan: Optional[str] = None,
    search: Optional[str] = None,
    current_user: UserInDB = Depends(require_admin),
):
    """List all users with filters"""
    users, total = await user_service.list_users(
        skip=skip, limit=limit, role=role, plan=plan, search=search
    )
    return {"users": users, "total": total, "skip": skip, "limit": limit}


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    data: UpdateUserRoleRequest,
    current_user: UserInDB = Depends(require_admin),
):
    """Update user role"""
    valid_roles = ["admin", "coach", "player", "analyst", "viewer"]
    if data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role invalido. Validos: {valid_roles}")

    success = await admin_service.update_user_role(user_id, data.role)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return {"message": "Role atualizado com sucesso"}


@router.put("/users/{user_id}/plan")
async def update_user_plan(
    user_id: str,
    data: UpdateUserPlanRequest,
    current_user: UserInDB = Depends(require_admin),
):
    """Update user subscription plan"""
    valid_plans = ["rally", "match_point", "grand_slam"]
    if data.plan not in valid_plans:
        raise HTTPException(status_code=400, detail=f"Plano invalido. Validos: {valid_plans}")

    success = await admin_service.update_user_plan(user_id, data.plan)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return {"message": "Plano atualizado com sucesso"}


@router.put("/users/{user_id}/active")
async def toggle_user_active(
    user_id: str,
    data: UpdateUserActiveRequest,
    current_user: UserInDB = Depends(require_admin),
):
    """Toggle user active status"""
    success = await admin_service.toggle_user_active(user_id, data.is_active)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return {"message": "Status atualizado com sucesso"}


@router.get("/subscriptions")
async def get_subscription_stats(current_user: UserInDB = Depends(require_admin)):
    """Get subscription statistics"""
    return await admin_service.get_subscription_stats()


@router.get("/logs")
async def get_activity_logs(
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: UserInDB = Depends(require_admin),
):
    """Get activity logs"""
    logs, total = await activity_log_service.get_all_logs(
        skip=skip, limit=limit, action=action, user_id=user_id
    )
    return {"logs": logs, "total": total, "skip": skip, "limit": limit}
