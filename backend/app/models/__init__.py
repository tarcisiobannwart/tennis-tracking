"""
Database models for tennis tracking application.

Modelos Pydantic (schemas) sao importados dos arquivos originais.
Modelos SQLAlchemy ORM sao importados do subpacote sql/ e dos modulos diretos.
"""

# SQLAlchemy ORM models (TT-119: users, orgs, auth)
from app.models.sql import (
    User,
    Organization,
    OrganizationInvite,
    SubscriptionEvent,
    ActivityLog,
    # TT-120: modelos de video, streams, analysis e player_stats
    Video,
    VideoStatusEnum,
    Stream,
    StreamStatusEnum,
    AnalysisTask,
    AnalysisStatusEnum,
    PlayerStats,
)

# SQLAlchemy ORM models (TT-121: training, events, point_history)
from app.models.training import (
    DrillType,
    TrainingSession,
    DrillCategory,
    DrillDifficulty,
    SessionStatus,
    SessionType,
)
from app.models.event import GameEvent, Event, EventType
from app.models.point_history import PointHistory, PointOutcome

__all__ = [
    # SQLAlchemy ORM models (TT-119)
    "User",
    "Organization",
    "OrganizationInvite",
    "SubscriptionEvent",
    "ActivityLog",
    # TT-120
    "Video",
    "VideoStatusEnum",
    "Stream",
    "StreamStatusEnum",
    "AnalysisTask",
    "AnalysisStatusEnum",
    "PlayerStats",
    # TT-121: training, events, point_history
    "DrillType",
    "TrainingSession",
    "DrillCategory",
    "DrillDifficulty",
    "SessionStatus",
    "SessionType",
    "GameEvent",
    "Event",
    "EventType",
    "PointHistory",
    "PointOutcome",
]