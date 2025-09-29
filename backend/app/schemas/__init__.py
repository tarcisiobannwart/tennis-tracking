"""
Pydantic schemas for data validation and serialization
"""

from .player import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerStats
from .match import MatchCreate, MatchUpdate, MatchResponse, MatchStats
from .point import PointCreate, PointResponse, PointEvent
from .event import EventCreate, EventResponse
from .training import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingSessionResponse,
    DrillTypeResponse,
    TrainingDrillCreate,
    TrainingDrillResponse
)
from .analytics import (
    PerformanceAnalytics,
    HeatmapData,
    PlayerComparison,
    TrendAnalysis
)
from .video import VideoUploadRequest, VideoAnalysisResponse, VideoAnalysisStatus

__all__ = [
    # Player schemas
    "PlayerCreate",
    "PlayerUpdate",
    "PlayerResponse",
    "PlayerStats",

    # Match schemas
    "MatchCreate",
    "MatchUpdate",
    "MatchResponse",
    "MatchStats",

    # Point schemas
    "PointCreate",
    "PointResponse",
    "PointEvent",

    # Event schemas
    "EventCreate",
    "EventResponse",

    # Training schemas
    "TrainingSessionCreate",
    "TrainingSessionUpdate",
    "TrainingSessionResponse",
    "DrillTypeResponse",
    "TrainingDrillCreate",
    "TrainingDrillResponse",

    # Analytics schemas
    "PerformanceAnalytics",
    "HeatmapData",
    "PlayerComparison",
    "TrendAnalysis",

    # Video schemas
    "VideoUploadRequest",
    "VideoAnalysisResponse",
    "VideoAnalysisStatus",
]