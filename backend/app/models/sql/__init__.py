"""
SQLAlchemy ORM models para PostgreSQL.

Modelos migrados de MongoDB/Pydantic para SQLAlchemy 2.0 style.
Os modelos Pydantic originais sao mantidos como schemas (Create/Response).
"""

from app.models.sql.user import User
from app.models.sql.organization import Organization, OrganizationInvite
from app.models.sql.subscription_event import SubscriptionEvent
from app.models.sql.activity_log import ActivityLog

# TT-120: Modelos de video, streams, analysis e player_stats
from app.models.sql.video import Video, VideoStatusEnum
from app.models.sql.stream import Stream, StreamStatusEnum
from app.models.sql.analysis import AnalysisTask, AnalysisStatusEnum
from app.models.sql.player_stats import PlayerStats

# TT-126: Modelo de embeddings de trajetórias com pgvector
from app.models.sql.trajectory_embedding import TrajectoryEmbedding

__all__ = [
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
    # TT-126
    "TrajectoryEmbedding",
]
