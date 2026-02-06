"""
Stream Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class StreamStatusEnum(str, Enum):
    """Stream status enumeration"""
    WAITING = "waiting"
    LIVE = "live"
    ENDED = "ended"


class PlatformEnum(str, Enum):
    """Device platform"""
    ANDROID = "android"
    IOS = "ios"
    UNKNOWN = "unknown"


class DeviceInfoSchema(BaseModel):
    """Device info from mobile camera"""
    platform: PlatformEnum = PlatformEnum.UNKNOWN
    model: Optional[str] = None
    resolution: Optional[str] = None
    os_version: Optional[str] = None


class StreamCreateRequest(BaseModel):
    """Request to create a new stream"""
    match_id: Optional[str] = None
    camera_label: str = "Camera 1"
    device_info: Optional[DeviceInfoSchema] = None

    @validator("camera_label")
    def validate_camera_label(cls, v):
        if len(v) > 50:
            raise ValueError("Camera label must be 50 characters or less")
        return v


class StreamUpdateRequest(BaseModel):
    """Request to update stream settings"""
    camera_label: Optional[str] = None
    device_info: Optional[DeviceInfoSchema] = None
    is_recording: Optional[bool] = None


class StreamResponse(BaseModel):
    """Stream response schema"""
    id: str
    match_id: Optional[str] = None
    user_id: str
    camera_label: str
    stream_key: str
    rtmp_url: str
    hls_url: str
    status: StreamStatusEnum
    device_info: DeviceInfoSchema
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    is_recording: bool = False
    viewer_count: int = 0

    class Config:
        from_attributes = True


class StreamListResponse(BaseModel):
    """Response for list of streams"""
    streams: List[StreamResponse]
    total: int
    active_count: int


class StreamRecordRequest(BaseModel):
    """Request to start/stop recording"""
    action: str  # "start" or "stop"

    @validator("action")
    def validate_action(cls, v):
        if v not in ["start", "stop"]:
            raise ValueError("Action must be 'start' or 'stop'")
        return v
