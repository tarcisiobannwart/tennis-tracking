"""
Users API routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_active_user, require_admin
from app.models.user import UserResponse, UserUpdate, UserInDB, PasswordChange
from app.models.sql.user import User
from app.services.user_service import user_service
from app.core.dependencies import get_plan_limits

router = APIRouter()


def _build_user_response(user: User) -> UserResponse:
    """Build UserResponse from User SQLAlchemy object"""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        fullName=user.full_name,
        role=user.role,
        isActive=user.is_active,
        profileImage=user.profile_image,
        phone=user.phone,
        country=user.country,
        language=user.language,
        preferences=user.preferences or {},
        createdAt=user.created_at,
        updatedAt=user.updated_at,
        lastLogin=user.last_login,
        subscription=user.subscription,
        organizationId=str(user.organization_id) if user.organization_id else None,
        organizationRole=user.organization_role,
        emailVerified=user.email_verified,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Get current user information"""
    user = await user_service.get_by_id(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return _build_user_response(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Update current user information"""
    update_dict = update_data.dict(exclude_unset=True)
    # Remove protected fields
    update_dict.pop("password", None)
    update_dict.pop("role", None)
    update_dict["updated_at"] = datetime.utcnow()

    # Convert camelCase to snake_case for DB fields
    field_mapping = {
        "fullName": "full_name",
        "profileImage": "profile_image",
    }
    for old_key, new_key in field_mapping.items():
        if old_key in update_dict:
            update_dict[new_key] = update_dict.pop(old_key)

    if update_dict:
        user = await user_service.update(db, current_user.id, update_dict)
    else:
        user = await user_service.get_by_id(db, current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return _build_user_response(user)


@router.post("/me/change-password")
async def change_password(
    data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Change current user password"""
    success = await user_service.change_password(
        db,
        current_user.id,
        data.current_password,
        data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Senha atual incorreta"
        )
    return {"message": "Senha alterada com sucesso"}


@router.get("/me/usage")
async def get_usage(
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Get current user usage stats and plan limits"""
    video_count = await user_service.get_video_count_this_month(db, current_user.id)
    limits = get_plan_limits(current_user)

    return {
        "videos_this_month": video_count,
        "videos_limit": limits["videos_per_month"],
        "max_video_duration": limits["max_video_duration"],
        "models": limits["models"],
        "history_days": limits["history_days"],
        "max_team_members": limits["max_team_members"],
        "api_access": limits["api_access"],
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Get user by ID"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario invalido")

    user = await user_service.get_by_id(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return _build_user_response(user)
