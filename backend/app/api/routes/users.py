"""
Users API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId

from app.core.mongodb import get_database
from app.core.auth import get_current_user
from app.models.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me")
async def update_current_user(
    update_data: dict,
    current_user=Depends(get_current_user)
):
    """Update current user information"""
    db = get_database()

    # Remove protected fields
    update_data.pop("_id", None)
    update_data.pop("email", None)
    update_data.pop("password", None)
    update_data.pop("role", None)

    result = await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": update_data}
    )

    if result.modified_count:
        updated_user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
        return updated_user

    return current_user