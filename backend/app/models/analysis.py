"""
Analysis models for MongoDB
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class AnalysisStatus(str):
    """Analysis task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BallDetection(BaseModel):
    """Ball detection data"""
    frameNumber: int
    x: float
    y: float
    confidence: float
    timestamp: float


class PlayerDetection(BaseModel):
    """Player detection data"""
    frameNumber: int
    playerId: str
    boundingBox: Dict[str, float]  # {x, y, width, height}
    position: Dict[str, float]  # {x, y} on court
    confidence: float
    timestamp: float


class CourtDetection(BaseModel):
    """Court detection data"""
    corners: List[Dict[str, float]]  # 4 corners of the court
    lines: List[Dict[str, Any]]  # detected court lines
    transformMatrix: Optional[List[List[float]]] = None
    confidence: float


class ShotDetection(BaseModel):
    """Shot detection data"""
    frameNumber: int
    shotType: str  # serve, forehand, backhand, volley, smash
    playerId: str
    ballPosition: Dict[str, float]
    playerPosition: Dict[str, float]
    speed: Optional[float] = None
    spin: Optional[str] = None
    timestamp: float


class Rally(BaseModel):
    """Rally information"""
    startFrame: int
    endFrame: int
    shots: List[ShotDetection]
    winner: Optional[str] = None
    endReason: Optional[str] = None  # winner, error, ace, double_fault


class AnalysisTask(BaseModel):
    """Analysis task model"""
    taskId: str = Field(default_factory=lambda: str(ObjectId()))
    videoId: str
    userId: str
    status: str = AnalysisStatus.PENDING
    progress: int = 0
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    error: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class AnalysisResult(BaseModel):
    """Complete analysis result model"""
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    taskId: str
    videoId: str
    matchId: Optional[str] = None

    # Detection data
    ballDetections: List[BallDetection] = []
    playerDetections: List[PlayerDetection] = []
    courtDetection: Optional[CourtDetection] = None
    shotDetections: List[ShotDetection] = []
    rallies: List[Rally] = []

    # Statistics
    totalFrames: int = 0
    processedFrames: int = 0
    detectionAccuracy: float = 0.0

    # Match statistics
    matchStats: Optional[Dict[str, Any]] = None
    playerStats: Optional[Dict[str, Any]] = None

    # Highlights
    highlights: List[Dict[str, Any]] = []

    # Metadata
    processingTime: float = 0.0  # in seconds
    modelVersions: Dict[str, str] = Field(default_factory=dict)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}