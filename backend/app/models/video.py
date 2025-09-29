"""
Video models for MongoDB
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class VideoStatus(str):
    """Video processing status"""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoBase(BaseModel):
    """Base video model"""
    filename: str
    originalFilename: str
    fileSize: int
    mimeType: str
    duration: Optional[float] = None  # in seconds
    resolution: Optional[str] = None
    fps: Optional[float] = None
    matchId: Optional[str] = None
    description: Optional[str] = None


class VideoCreate(VideoBase):
    """Video creation model"""
    userId: str
    uploadPath: str


class VideoInDB(VideoBase):
    """Video model as stored in database"""
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    userId: str
    uploadPath: str
    processedPath: Optional[str] = None
    thumbnailPath: Optional[str] = None
    status: str = VideoStatus.UPLOADING
    processingProgress: int = 0
    metadata: Optional[Dict[str, Any]] = None
    analysisResults: Optional[Dict[str, Any]] = None
    uploadedAt: datetime = Field(default_factory=datetime.utcnow)
    processedAt: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class VideoResponse(VideoBase):
    """Video response model"""
    id: str
    userId: str
    status: str
    processingProgress: int
    uploadedAt: datetime
    processedAt: Optional[datetime] = None
    thumbnailUrl: Optional[str] = None
    videoUrl: Optional[str] = None
    analysisAvailable: bool = False