"""
Users API routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional
from bson import ObjectId
from datetime import datetime

from app.core.mongodb import get_database, get_collection
from app.core.auth import get_current_user, get_current_active_user, require_admin
from app.models.user import UserResponse, UserUpdate, UserInDB, PasswordChange
from app.services.user_service import user_service
from app.core.dependencies import get_plan_limits

router = APIRouter()


def _build_user_response(user: dict) -> UserResponse:
    """Build UserResponse from user dict"""
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        fullName=user["fullName"],
        role=user.get("role", "viewer"),
        isActive=user.get("isActive", True),
        profileImage=user.get("profileImage"),
        phone=user.get("phone"),
        country=user.get("country"),
        language=user.get("language", "pt-BR"),
        preferences=user.get("preferences", {}),
        createdAt=user["createdAt"],
        updatedAt=user["updatedAt"],
        lastLogin=user.get("lastLogin"),
        subscription=user.get("subscription"),
        organizationId=user.get("organizationId"),
        organizationRole=user.get("organizationRole"),
        emailVerified=user.get("emailVerified", False),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information"""
    users = get_collection("users")
    user = await users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    user["_id"] = str(user["_id"])
    return _build_user_response(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update current user information"""
    users = get_collection("users")

    update_dict = update_data.dict(exclude_unset=True)
    # Remove protected fields
    update_dict.pop("_id", None)
    update_dict.pop("password", None)
    update_dict.pop("role", None)
    update_dict["updatedAt"] = datetime.utcnow()

    if update_dict:
        await users.update_one(
            {"_id": current_user.id},
            {"$set": update_dict}
        )

    user = await users.find_one({"_id": current_user.id})
    user["_id"] = str(user["_id"])
    return _build_user_response(user)


@router.post("/me/change-password")
async def change_password(
    data: PasswordChange,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Change current user password"""
    success = await user_service.change_password(
        str(current_user.id),
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
async def get_usage(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user usage stats and plan limits"""
    video_count = await user_service.get_video_count_this_month(str(current_user.id))
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
async def get_user(user_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """Get user by ID"""
    users = get_collection("users")
    user = await users.find_one({"_id": user_id})
    if not user:
        # Try ObjectId
        try:
            user = await users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            pass
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    user["_id"] = str(user["_id"])
    return _build_user_response(user)
