"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
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
from app.core.middleware import limiter
from app.models.user import (
    UserCreate,
    UserResponse,
    UserInDB,
    UserSubscription,
    Token,
    UserLogin,
    PasswordResetRequest,
    PasswordReset,
)
from app.services.user_service import user_service
from app.services.email_service import email_service
from app.services.activity_log_service import activity_log_service


router = APIRouter(tags=["authentication"])


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


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, request: Request):
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
            detail="Usuario com este email ou username ja existe"
        )

    # Create user with default subscription
    user_dict = user_data.dict()
    user_dict["password"] = get_password_hash(user_data.password)
    user_dict["createdAt"] = datetime.utcnow()
    user_dict["updatedAt"] = datetime.utcnow()
    user_dict["emailVerified"] = False
    user_dict["subscription"] = UserSubscription().dict()

    result = await users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)

    # Create tokens
    token_data = {
        "sub": str(result.inserted_id),
        "username": user_data.username,
        "role": user_data.role
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token
    await users.update_one(
        {"_id": result.inserted_id},
        {"$set": {"refreshToken": refresh_token}}
    )

    # Send verification email
    verification_token = await user_service.create_email_verification_token(str(result.inserted_id))
    await email_service.send_email_verification(user_data.email, verification_token)

    # Log activity
    await activity_log_service.log(
        user_id=str(result.inserted_id),
        action="register",
        resource="user",
        resource_id=str(result.inserted_id),
        ip_address=request.client.host if request.client else None,
    )

    user_response = _build_user_response(user_dict)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response,
    )


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username and password"""
    users = get_collection("users")

    # Find user by username or email
    user = await users.find_one({
        "$or": [
            {"username": form_data.username},
            {"email": form_data.username},
        ]
    })

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conta de usuario desativada"
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

    # Log activity
    await activity_log_service.log(
        user_id=str(user["_id"]),
        action="login",
        resource="user",
        ip_address=request.client.host if request.client else None,
    )

    user["_id"] = str(user["_id"])
    user_response = _build_user_response(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response,
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
                detail="Token de refresh invalido"
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

        user["_id"] = str(user["_id"])
        user_response = _build_user_response(user)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=user_response,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh invalido"
        )


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_active_user)):
    """Logout current user (invalidate refresh token)"""
    users = get_collection("users")

    await users.update_one(
        {"_id": current_user.id},
        {"$set": {"refreshToken": None}}
    )

    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information"""
    users = get_collection("users")
    user = await users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    user["_id"] = str(user["_id"])
    return _build_user_response(user)


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: PasswordResetRequest):
    """Request password reset email"""
    token = await user_service.create_password_reset_token(data.email)
    if token:
        await email_service.send_password_reset(data.email, token)

    # Always return success to avoid email enumeration
    return {"message": "Se o email existir, um link de redefinicao sera enviado"}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, data: PasswordReset):
    """Reset password using token"""
    success = await user_service.reset_password(data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token invalido ou expirado"
        )
    return {"message": "Senha redefinida com sucesso"}


@router.post("/verify-email")
async def verify_email(token: str):
    """Verify email address"""
    success = await user_service.verify_email(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificacao invalido"
        )
    return {"message": "Email verificado com sucesso"}
