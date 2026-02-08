"""
Organization Pydantic models
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class OrgMember(BaseModel):
    """Organization member"""
    userId: str
    role: str = "member"
    joinedAt: datetime = Field(default_factory=datetime.utcnow)


class OrganizationBase(BaseModel):
    """Base organization model"""
    name: str
    slug: str


class OrganizationCreate(BaseModel):
    """Organization creation model"""
    name: str


class OrganizationInDB(OrganizationBase):
    """Organization as stored in database"""
    ownerId: str
    plan: str = "grand_slam"
    maxMembers: int = 10
    members: List[OrgMember] = Field(default_factory=list)
    stripeCustomerId: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class OrganizationResponse(OrganizationBase):
    """Organization response model"""
    id: str
    ownerId: str
    plan: str
    maxMembers: int
    members: List[OrgMember] = []
    createdAt: datetime
    updatedAt: datetime


class OrganizationUpdate(BaseModel):
    """Organization update model"""
    name: Optional[str] = None


class InviteStatus(str, Enum):
    """Invite status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class OrganizationInvite(BaseModel):
    """Organization invite model"""
    organizationId: str
    email: EmailStr
    role: str = "member"
    token: str
    invitedBy: str
    status: InviteStatus = InviteStatus.PENDING
    expiresAt: datetime
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class InviteCreate(BaseModel):
    """Invite creation model"""
    email: EmailStr
    role: str = "member"
