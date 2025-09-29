"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_active_user
)
from app.core.mongodb import get_collection
from app.models.user import (
    UserCreate,
    UserResponse,
    UserInDB,
    Token,
    UserLogin
)


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    users = get_collection("users")

    # Check if user exists
    existing_user = await users.find_one({"$or": [
        {"email": user_data.email},
        {"username": user_data.username}
    ]})

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Create new user
    user_dict = user_data.dict()
    user_dict["password"] = get_password_hash(user_data.password)
    user_dict["createdAt"] = datetime.utcnow()
    user_dict["updatedAt"] = datetime.utcnow()

    # Insert user
    result = await users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)

    return UserResponse(id=str(result.inserted_id), **user_data.dict(exclude={"password"}))


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username and password"""
    users = get_collection("users")

    # Find user
    user = await users.find_one({"username": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )

    # Update last login
    await users.update_one(
        {"_id": user["_id"]},
        {"$set": {"lastLogin": datetime.utcnow()}}
    )

    # Create tokens
    token_data = {
        "sub": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "viewer")
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token
    await users.update_one(
        {"_id": user["_id"]},
        {"$set": {"refreshToken": refresh_token}}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    from app.core.auth import verify_token

    try:
        # Verify refresh token
        token_data = verify_token(refresh_token)

        # Check if it's a refresh token
        users = get_collection("users")
        user = await users.find_one({
            "_id": token_data.user_id,
            "refreshToken": refresh_token
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Create new tokens
        new_token_data = {
            "sub": str(user["_id"]),
            "username": user["username"],
            "role": user.get("role", "viewer")
        }

        new_access_token = create_access_token(new_token_data)
        new_refresh_token = create_refresh_token(new_token_data)

        # Update refresh token in database
        await users.update_one(
            {"_id": user["_id"]},
            {"$set": {"refreshToken": new_refresh_token}}
        )

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_active_user)):
    """Logout current user (invalidate refresh token)"""
    users = get_collection("users")

    await users.update_one(
        {"_id": current_user.id},
        {"$set": {"refreshToken": None}}
    )

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        fullName=current_user.fullName,
        role=current_user.role,
        isActive=current_user.isActive,
        createdAt=current_user.createdAt,
        updatedAt=current_user.updatedAt,
        lastLogin=current_user.lastLogin
    )