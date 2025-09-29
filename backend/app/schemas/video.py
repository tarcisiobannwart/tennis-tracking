"""
Video processing Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class VideoAnalysisStatusEnum(str, Enum):
    """Video analysis status enumeration"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoFormatEnum(str, Enum):
    """Supported video formats"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"


class VideoUploadRequest(BaseModel):
    """Schema for video upload request"""
    filename: str
    file_size: int
    match_id: Optional[str] = None
    analysis_options: Optional[Dict[str, Any]] = None

    @validator("file_size")
    def validate_file_size(cls, v):
        max_size = 500 * 1024 * 1024  # 500MB
        if v > max_size:
            raise ValueError(f"File size {v} exceeds maximum allowed size {max_size}")
        return v

    @validator("filename")
    def validate_filename(cls, v):
        allowed_extensions = [".mp4", ".avi", ".mov", ".mkv"]
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"File format not supported. Allowed: {allowed_extensions}")
        return v


class VideoUploadResponse(BaseModel):
    """Schema for video upload response"""
    task_id: str
    upload_url: str
    expires_at: datetime
    chunk_size: int = 1024 * 1024  # 1MB chunks

    class Config:
        from_attributes = True


class VideoAnalysisOptions(BaseModel):
    """Schema for video analysis configuration"""
    enable_ball_tracking: bool = True
    enable_player_detection: bool = True
    enable_court_detection: bool = True
    enable_bounce_detection: bool = True
    enable_serve_analysis: bool = True
    enable_rally_analysis: bool = True
    generate_minimap: bool = False
    extract_highlights: bool = False
    frame_rate: Optional[int] = None
    quality: str = "high"  # "low", "medium", "high"

    @validator("quality")
    def validate_quality(cls, v):
        if v not in ["low", "medium", "high"]:
            raise ValueError("quality must be 'low', 'medium', or 'high'")
        return v


class VideoAnalysisProgress(BaseModel):
    """Schema for video analysis progress"""
    task_id: str
    status: VideoAnalysisStatusEnum
    progress: int  # 0-100
    current_stage: str
    estimated_time_remaining: Optional[int] = None  # seconds
    processed_frames: int = 0
    total_frames: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BallTrackingData(BaseModel):
    """Schema for ball tracking results"""
    frame_number: int
    timestamp: float
    x: float
    y: float
    confidence: float
    velocity: Optional[Dict[str, float]] = None
    is_bounce: bool = False


class PlayerDetectionData(BaseModel):
    """Schema for player detection results"""
    frame_number: int
    timestamp: float
    player_id: int
    bounding_box: Dict[str, float]  # {"x", "y", "width", "height"}
    confidence: float
    court_position: Optional[Dict[str, float]] = None


class CourtDetectionData(BaseModel):
    """Schema for court detection results"""
    frame_number: int
    timestamp: float
    court_lines: List[Dict[str, Any]]
    homography_matrix: List[List[float]]
    confidence: float


class VideoAnalysisResult(BaseModel):
    """Schema for complete video analysis results"""
    ball_tracking: List[BallTrackingData] = []
    player_detection: List[PlayerDetectionData] = []
    court_detection: List[CourtDetectionData] = []
    rally_analysis: List[Dict[str, Any]] = []
    serve_analysis: List[Dict[str, Any]] = []
    bounce_detection: List[Dict[str, Any]] = []
    highlights: List[Dict[str, Any]] = []
    statistics: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class VideoAnalysisResponse(BaseModel):
    """Schema for video analysis response"""
    task_id: str
    match_id: Optional[str] = None
    status: VideoAnalysisStatusEnum
    progress: int
    result: Optional[VideoAnalysisResult] = None
    output_video_path: Optional[str] = None
    minimap_video_path: Optional[str] = None
    analysis_summary: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None  # seconds
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VideoAnalysisStatus(BaseModel):
    """Schema for video analysis status check"""
    task_id: str
    status: VideoAnalysisStatusEnum
    progress: int
    message: str
    estimated_completion: Optional[datetime] = None

    class Config:
        from_attributes = True