"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    verify_token,
)
from app.core.database import get_db
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
from app.models.sql.user import User as SQLUser, SubscriptionPlan, SubscriptionStatus
from app.services.user_service import user_service
from app.services.email_service import email_service
from app.services.activity_log_service import activity_log_service


router = APIRouter(tags=["authentication"])


def _build_user_response_from_sql(user: SQLUser) -> UserResponse:
    """Build UserResponse from SQLAlchemy User model"""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        fullName=user.full_name,
        role=user.role.value if hasattr(user.role, 'value') else user.role,
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


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_email = await user_service.get_by_email(db, user_data.email)
    existing_username = await user_service.get_by_username(db, user_data.username)

    if existing_email or existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario com este email ou username ja existe"
        )

    # Create user
    user = await user_service.create(db, user_data)

    # Create tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token
    await user_service.update_refresh_token(db, user.id, refresh_token)

    # Send verification email
    verification_token = await user_service.create_email_verification_token(db, user.id)
    if verification_token:
        await email_service.send_email_verification(user_data.email, verification_token)

    # Log activity
    await activity_log_service.log(
        db=db,
        user_id=user.id,
        action="register",
        resource="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )

    # Refresh user to load any expired attributes (onupdate columns)
    await db.refresh(user)
    user_response = _build_user_response_from_sql(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response,
    )


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Login with username and password"""
    # Find user by username or email
    user = await user_service.get_by_username_or_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conta de usuario desativada"
        )

    # Update last login
    await user_service.update_last_login(db, user.id)

    # Create tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token
    await user_service.update_refresh_token(db, user.id, refresh_token)

    # Log activity
    await activity_log_service.log(
        db=db,
        user_id=user.id,
        action="login",
        resource="user",
        ip_address=request.client.host if request.client else None,
    )

    # Refresh user to load any expired attributes (onupdate columns)
    await db.refresh(user)
    user_response = _build_user_response_from_sql(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        token_data = verify_token(refresh_token)

        import uuid as uuid_mod
        try:
            user_uuid = uuid_mod.UUID(token_data.user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh invalido"
            )

        # Check user and refresh token match
        user = await user_service.get_by_id(db, user_uuid)

        if not user or user.refresh_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh invalido"
            )

        # Create new tokens
        new_token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
        }

        new_access_token = create_access_token(new_token_data)
        new_refresh_token = create_refresh_token(new_token_data)

        # Update refresh token in database
        await user_service.update_refresh_token(db, user.id, new_refresh_token)

        # Refresh user to load any expired attributes (onupdate columns)
        await db.refresh(user)
        user_response = _build_user_response_from_sql(user)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=user_response,
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh invalido"
        )


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Logout current user (invalidate refresh token)"""
    import uuid as uuid_mod
    user_uuid = uuid_mod.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    await user_service.update_refresh_token(db, user_uuid, None)
    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Get current user information"""
    import uuid as uuid_mod
    user_uuid = uuid_mod.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    user = await user_service.get_by_id(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return _build_user_response_from_sql(user)


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Request password reset email"""
    token = await user_service.create_password_reset_token(db, data.email)
    if token:
        await email_service.send_password_reset(data.email, token)

    # Always return success to avoid email enumeration
    return {"message": "Se o email existir, um link de redefinicao sera enviado"}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, data: PasswordReset, db: AsyncSession = Depends(get_db)):
    """Reset password using token"""
    success = await user_service.reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token invalido ou expirado"
        )
    return {"message": "Senha redefinida com sucesso"}


@router.post("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify email address"""
    success = await user_service.verify_email(db, token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificacao invalido"
        )
    return {"message": "Email verificado com sucesso"}
