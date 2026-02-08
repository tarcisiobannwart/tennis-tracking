"""
Stream Pydantic models - Live camera streaming
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class StreamStatus(str):
    """Stream status values"""
    WAITING = "waiting"
    LIVE = "live"
    ENDED = "ended"


class DeviceInfo(BaseModel):
    """Device information from mobile camera"""
    platform: str = "unknown"  # android, ios
    model: Optional[str] = None
    resolution: Optional[str] = None
    os_version: Optional[str] = None


class StreamBase(BaseModel):
    """Base stream model"""
    matchId: Optional[str] = None
    cameraLabel: str = "Camera 1"
    deviceInfo: DeviceInfo = Field(default_factory=DeviceInfo)


class StreamCreate(StreamBase):
    """Stream creation model"""
    userId: str


class StreamInDB(StreamBase):
    """Stream model as stored in database"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    userId: str
    streamKey: str
    rtmpUrl: str
    hlsUrl: str
    rtspUrl: str
    status: str = StreamStatus.WAITING
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    isRecording: bool = False
    viewerCount: int = 0
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class StreamResponse(BaseModel):
    """Stream response model"""
    id: str
    matchId: Optional[str] = None
    userId: str
    cameraLabel: str
    streamKey: str
    rtmpUrl: str
    hlsUrl: str
    status: str
    deviceInfo: DeviceInfo
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    createdAt: datetime
    isRecording: bool = False
    viewerCount: int = 0
