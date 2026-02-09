"""
User Pydantic models
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    COACH = "coach"
    PLAYER = "player"
    ANALYST = "analyst"
    VIEWER = "viewer"


class SubscriptionPlan(str, Enum):
    """Subscription plan enumeration"""
    RALLY = "rally"
    MATCH_POINT = "match_point"
    GRAND_SLAM = "grand_slam"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"


class OrganizationRole(str, Enum):
    """Organization role enumeration"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class UserSubscription(BaseModel):
    """Embedded subscription info in user document"""
    plan: SubscriptionPlan = SubscriptionPlan.RALLY
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    stripeCustomerId: Optional[str] = None
    stripeSubscriptionId: Optional[str] = None
    currentPeriodStart: Optional[datetime] = None
    currentPeriodEnd: Optional[datetime] = None
    cancelAtPeriodEnd: bool = False
    trialEnd: Optional[datetime] = None


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str
    fullName: str
    role: str = UserRole.VIEWER.value
    isActive: bool = True
    profileImage: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    language: str = "pt-BR"
    preferences: Optional[dict] = Field(default_factory=dict)


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserInDB(UserBase):
    """User model as stored in database"""
    id: Optional[str] = Field(default=None)
    password: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    lastLogin: Optional[datetime] = None
    refreshToken: Optional[str] = None
    # Subscription
    subscription: Optional[UserSubscription] = Field(default_factory=UserSubscription)
    # Organization
    organizationId: Optional[str] = None
    organizationRole: Optional[str] = None
    # Email verification
    emailVerified: bool = False
    emailVerificationToken: Optional[str] = None
    # Password reset
    passwordResetToken: Optional[str] = None
    passwordResetExpires: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "fullName": "John Doe",
                "role": "player",
                "isActive": True,
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }


class UserResponse(UserBase):
    """User response model (without password)"""
    id: str
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime] = None
    subscription: Optional[UserSubscription] = None
    organizationId: Optional[str] = None
    organizationRole: Optional[str] = None
    emailVerified: bool = False


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    fullName: Optional[str] = None
    profileImage: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    preferences: Optional[dict] = None


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str


class Token(BaseModel):
    """Token model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class TokenData(BaseModel):
    """Token data model"""
    user_id: str
    username: str
    role: str
    exp: datetime


class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset model"""
    token: str
    new_password: str


class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str
    new_password: str
