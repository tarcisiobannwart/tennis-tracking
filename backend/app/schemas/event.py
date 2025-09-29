"""
Event Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema"""
    event_type: str
    event_data: Optional[Dict[str, Any]] = None
    court_x: Optional[float] = None
    court_y: Optional[float] = None
    confidence: Optional[float] = None
    manual_entry: bool = False


class EventCreate(EventBase):
    """Schema for creating an event"""
    match_id: str
    point_id: Optional[str] = None
    player_id: Optional[str] = None
    video_timestamp: Optional[float] = None


class EventResponse(EventBase):
    """Schema for event response"""
    id: str
    match_id: str
    point_id: Optional[str] = None
    player_id: Optional[str] = None
    timestamp: datetime
    video_timestamp: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True