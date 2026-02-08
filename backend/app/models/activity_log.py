"""
Activity log Pydantic models
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ActivityLog(BaseModel):
    """Activity log entry"""
    userId: str
    action: str  # login, logout, upload, delete, subscribe, etc.
    resource: str  # user, video, match, subscription, organization
    resourceId: Optional[str] = None
    details: Optional[dict] = Field(default_factory=dict)
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
