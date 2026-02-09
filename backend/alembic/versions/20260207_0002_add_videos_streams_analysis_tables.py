"""Adicionar tabelas videos, streams, analysis_tasks e player_stats

Revision ID: 0002_media_analysis
Revises: 0001_initial_setup
Create Date: 2026-02-07

Migration TT-120: Migrar modelos MongoDB de videos, streams e analysis
para SQLAlchemy/PostgreSQL.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = "0002_media_analysis"
down_revision: Union[str, None] = "0002_match_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Criar tabelas videos, streams, analysis_tasks e player_stats."""

    # ── Tabela: videos ──────────────────────────────────────────────
    op.create_table(
        "videos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", sa.String(255), nullable=True),
        # File info
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        # Video metadata
        sa.Column("duration", sa.Float, nullable=True),
        sa.Column("resolution", sa.String(20), nullable=True),
        sa.Column("fps", sa.Float, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        # Paths
        sa.Column("upload_path", sa.String(1000), nullable=False),
        sa.Column("processed_path", sa.String(1000), nullable=True),
        sa.Column("thumbnail_path", sa.String(1000), nullable=True),
        # Status
        sa.Column("status", sa.String(20), nullable=False, server_default="uploading"),
        sa.Column("processing_progress", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error", sa.Text, nullable=True),
        # JSONB
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("analysis_results", JSONB, nullable=True),
        # Timestamps
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_videos_user_id", "videos", ["user_id"])
    op.create_index("ix_videos_status", "videos", ["status"])
    op.create_index("ix_videos_match_id", "videos", ["match_id"])
    op.create_index("ix_videos_uploaded_at", "videos", ["uploaded_at"])

    # ── Tabela: streams ─────────────────────────────────────────────
    op.create_table(
        "streams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", sa.String(255), nullable=True),
        # Stream identification
        sa.Column("stream_key", sa.String(255), nullable=False, unique=True),
        sa.Column("camera_label", sa.String(100), nullable=False, server_default="Camera 1"),
        # URLs
        sa.Column("rtmp_url", sa.String(1000), nullable=False),
        sa.Column("hls_url", sa.String(1000), nullable=False),
        sa.Column("rtsp_url", sa.String(1000), nullable=False),
        # Status
        sa.Column("status", sa.String(20), nullable=False, server_default="waiting"),
        sa.Column("is_recording", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("viewer_count", sa.Integer, nullable=False, server_default="0"),
        # JSONB
        sa.Column("device_info", JSONB, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        # Timestamps
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_streams_user_id", "streams", ["user_id"])
    op.create_index("ix_streams_status", "streams", ["status"])
    op.create_index("ix_streams_stream_key", "streams", ["stream_key"], unique=True)
    op.create_index("ix_streams_match_id", "streams", ["match_id"])
    op.create_index("ix_streams_created_at", "streams", ["created_at"])

    # ── Tabela: analysis_tasks ──────────────────────────────────────
    op.create_table(
        "analysis_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("video_id", UUID(as_uuid=True), sa.ForeignKey("videos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", sa.String(255), nullable=True),
        # Status
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("progress", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error", sa.Text, nullable=True),
        # JSONB config
        sa.Column("config", JSONB, nullable=True),
        # Detection results (JSONB)
        sa.Column("ball_detections", JSONB, nullable=True),
        sa.Column("player_detections", JSONB, nullable=True),
        sa.Column("court_detection", JSONB, nullable=True),
        sa.Column("shot_detections", JSONB, nullable=True),
        sa.Column("rallies", JSONB, nullable=True),
        # Statistics
        sa.Column("total_frames", sa.Integer, nullable=False, server_default="0"),
        sa.Column("processed_frames", sa.Integer, nullable=False, server_default="0"),
        sa.Column("detection_accuracy", sa.Float, nullable=False, server_default="0.0"),
        # Match and player stats (JSONB)
        sa.Column("match_stats", JSONB, nullable=True),
        sa.Column("player_stats_data", JSONB, nullable=True),
        # Highlights
        sa.Column("highlights", JSONB, nullable=True),
        # Processing metadata
        sa.Column("processing_time", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("model_versions", JSONB, nullable=True),
        # Timestamps
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_analysis_tasks_video_id", "analysis_tasks", ["video_id"])
    op.create_index("ix_analysis_tasks_user_id", "analysis_tasks", ["user_id"])
    op.create_index("ix_analysis_tasks_status", "analysis_tasks", ["status"])
    op.create_index("ix_analysis_tasks_created_at", "analysis_tasks", ["created_at"])

    # ── Tabela: player_stats ────────────────────────────────────────
    op.create_table(
        "player_stats",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("player_id", sa.String, sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("match_id", sa.String, sa.ForeignKey("matches.id", ondelete="CASCADE"), nullable=False),
        # Serve statistics
        sa.Column("first_serve_pct", sa.Float, nullable=True),
        sa.Column("second_serve_pct", sa.Float, nullable=True),
        sa.Column("aces", sa.Integer, nullable=True),
        sa.Column("double_faults", sa.Integer, nullable=True),
        sa.Column("avg_first_serve_speed", sa.Float, nullable=True),
        sa.Column("avg_second_serve_speed", sa.Float, nullable=True),
        sa.Column("max_serve_speed", sa.Float, nullable=True),
        # Rally statistics
        sa.Column("total_shots", sa.Integer, nullable=True),
        sa.Column("forehand_count", sa.Integer, nullable=True),
        sa.Column("backhand_count", sa.Integer, nullable=True),
        sa.Column("volley_count", sa.Integer, nullable=True),
        sa.Column("smash_count", sa.Integer, nullable=True),
        sa.Column("winners", sa.Integer, nullable=True),
        sa.Column("unforced_errors", sa.Integer, nullable=True),
        # Movement statistics
        sa.Column("total_distance_m", sa.Float, nullable=True),
        sa.Column("avg_speed_kmh", sa.Float, nullable=True),
        sa.Column("max_speed_kmh", sa.Float, nullable=True),
        # Points statistics
        sa.Column("points_won", sa.Integer, nullable=True),
        sa.Column("points_lost", sa.Integer, nullable=True),
        sa.Column("break_points_won", sa.Integer, nullable=True),
        sa.Column("break_points_total", sa.Integer, nullable=True),
        # JSONB
        sa.Column("extended_stats", JSONB, nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_player_stats_player_id", "player_stats", ["player_id"])
    op.create_index("ix_player_stats_match_id", "player_stats", ["match_id"])
    op.create_index("ix_player_stats_player_match", "player_stats", ["player_id", "match_id"], unique=True)
    op.create_index("ix_player_stats_created_at", "player_stats", ["created_at"])


def downgrade() -> None:
    """Remover tabelas videos, streams, analysis_tasks e player_stats."""
    # Remover na ordem inversa (por causa de FKs)
    op.drop_table("player_stats")
    op.drop_table("analysis_tasks")
    op.drop_table("streams")
    op.drop_table("videos")
