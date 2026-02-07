"""Criar tabelas drill_types, training_sessions, game_events, point_history

Revision ID: 0002_training_events_ph
Revises: 0001_initial_setup
Create Date: 2026-02-07

Migra modelos de training, game_events e point_history para PostgreSQL.
Cria enums PostgreSQL: drill_category, drill_difficulty, session_type,
session_status, event_type, point_outcome.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY

# revision identifiers, used by Alembic.
revision: str = "0002_training_events_ph"
down_revision: Union[str, None] = "0001_initial_setup"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum definitions
drill_category_enum = sa.Enum(
    "technique", "fitness", "tactical", "serve", "return",
    "volley", "footwork", "mental",
    name="drill_category",
)

drill_difficulty_enum = sa.Enum(
    "beginner", "intermediate", "advanced", "professional",
    name="drill_difficulty",
)

session_type_enum = sa.Enum(
    "practice", "match_prep", "recovery", "fitness", "technique", "tactical",
    name="session_type",
)

session_status_enum = sa.Enum(
    "planned", "in_progress", "completed", "cancelled",
    name="session_status",
)

event_type_enum = sa.Enum(
    "point_started", "point_scored", "game_won", "set_won", "match_won",
    "serve", "shot", "ball_bounce", "player_position", "court_detection",
    "error", "let", "challenge",
    name="event_type",
)

point_outcome_enum = sa.Enum(
    "ace", "winner", "unforced_error", "forced_error", "double_fault",
    "service_winner", "return_winner", "volley_winner", "smash_winner",
    "drop_shot_winner", "let", "net", "out", "long", "wide",
    name="point_outcome",
)


def upgrade() -> None:
    """Criar tabelas e enums para training, events e point_history."""

    # Criar enums no PostgreSQL
    drill_category_enum.create(op.get_bind(), checkfirst=True)
    drill_difficulty_enum.create(op.get_bind(), checkfirst=True)
    session_type_enum.create(op.get_bind(), checkfirst=True)
    session_status_enum.create(op.get_bind(), checkfirst=True)
    event_type_enum.create(op.get_bind(), checkfirst=True)
    point_outcome_enum.create(op.get_bind(), checkfirst=True)

    # ========== drill_types ==========
    op.create_table(
        "drill_types",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", drill_category_enum, nullable=False),
        sa.Column("difficulty", drill_difficulty_enum, nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("equipment_needed", ARRAY(sa.String), nullable=True),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_drill_types_category", "drill_types", ["category"])
    op.create_index("ix_drill_types_difficulty", "drill_types", ["difficulty"])
    op.create_index("ix_drill_types_name", "drill_types", ["name"])

    # ========== training_sessions ==========
    op.create_table(
        "training_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "player_id",
            sa.String,
            sa.ForeignKey("players.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "session_type",
            session_type_enum,
            nullable=False,
            server_default="practice",
        ),
        sa.Column(
            "status",
            session_status_enum,
            nullable=False,
            server_default="planned",
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("objectives", ARRAY(sa.String), nullable=True),
        sa.Column("focus_areas", ARRAY(sa.String), nullable=True),
        sa.Column("coach_name", sa.String(100), nullable=True),
        sa.Column("coach_notes", sa.Text, nullable=True),
        sa.Column("intensity_level", sa.Integer, nullable=True),
        sa.Column("effort_rating", sa.Integer, nullable=True),
        sa.Column("fatigue_level", sa.Integer, nullable=True),
        sa.Column("video_file_path", sa.String(500), nullable=True),
        sa.Column("analysis_data", JSONB, nullable=True),
        sa.Column("session_notes", sa.Text, nullable=True),
        sa.Column("player_feedback", sa.Text, nullable=True),
        sa.Column("drills", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_training_sessions_player_id", "training_sessions", ["player_id"]
    )
    op.create_index(
        "ix_training_sessions_status", "training_sessions", ["status"]
    )
    op.create_index(
        "ix_training_sessions_session_type",
        "training_sessions",
        ["session_type"],
    )
    op.create_index(
        "ix_training_sessions_scheduled_at",
        "training_sessions",
        ["scheduled_at"],
    )

    # ========== game_events ==========
    op.create_table(
        "game_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "match_id",
            sa.String,
            sa.ForeignKey("matches.id"),
            nullable=False,
        ),
        sa.Column(
            "point_id",
            sa.String,
            sa.ForeignKey("points.id"),
            nullable=True,
        ),
        sa.Column("event_type", event_type_enum, nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "video_timestamp",
            sa.Float,
            nullable=True,
            comment="Segundos desde o inicio do video",
        ),
        sa.Column(
            "player_id",
            sa.String,
            sa.ForeignKey("players.id"),
            nullable=True,
        ),
        sa.Column("event_data", JSONB, nullable=True),
        sa.Column("court_x", sa.Float, nullable=True),
        sa.Column("court_y", sa.Float, nullable=True),
        sa.Column(
            "confidence",
            sa.Float,
            nullable=True,
            comment="Score de confianca do modelo AI/ML",
        ),
        sa.Column(
            "manual_entry",
            sa.Boolean,
            server_default=sa.text("false"),
            comment="Entrada manual vs automatizada",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_game_events_match_id", "game_events", ["match_id"])
    op.create_index("ix_game_events_event_type", "game_events", ["event_type"])
    op.create_index("ix_game_events_player_id", "game_events", ["player_id"])
    op.create_index("ix_game_events_timestamp", "game_events", ["timestamp"])

    # ========== point_history ==========
    op.create_table(
        "point_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "match_id",
            sa.String,
            sa.ForeignKey("matches.id"),
            nullable=False,
        ),
        sa.Column("set_number", sa.Integer, nullable=False),
        sa.Column("game_number", sa.Integer, nullable=False),
        sa.Column("point_number", sa.Integer, nullable=False),
        # Placar JSONB
        sa.Column(
            "score_before",
            JSONB,
            nullable=True,
            comment="Placar antes do ponto",
        ),
        sa.Column(
            "score_after",
            JSONB,
            nullable=True,
            comment="Placar apos o ponto",
        ),
        sa.Column(
            "set_score_before",
            JSONB,
            nullable=True,
            comment="Placar de games no set antes do ponto",
        ),
        sa.Column(
            "set_score_after",
            JSONB,
            nullable=True,
            comment="Placar de games no set apos o ponto",
        ),
        # Jogadores
        sa.Column(
            "server_player_id",
            sa.String,
            sa.ForeignKey("players.id"),
            nullable=False,
        ),
        sa.Column(
            "receiver_player_id",
            sa.String,
            sa.ForeignKey("players.id"),
            nullable=False,
        ),
        sa.Column(
            "point_winner_id",
            sa.String,
            sa.ForeignKey("players.id"),
            nullable=False,
        ),
        # Resultado
        sa.Column("outcome", point_outcome_enum, nullable=False),
        sa.Column("winning_shot", sa.String(50), nullable=True),
        sa.Column("error_type", sa.String(50), nullable=True),
        # Rally
        sa.Column("rally_length", sa.Integer, server_default=sa.text("0")),
        sa.Column(
            "rally_duration",
            sa.Float,
            nullable=True,
            comment="Duracao do rally em segundos",
        ),
        # Saque
        sa.Column(
            "is_first_serve",
            sa.Boolean,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "serve_speed",
            sa.Float,
            nullable=True,
            comment="Velocidade do saque em km/h",
        ),
        sa.Column(
            "serve_placement",
            sa.String(20),
            nullable=True,
            comment="Posicao do saque (wide, body, T)",
        ),
        sa.Column(
            "is_serve_in",
            sa.Boolean,
            server_default=sa.text("true"),
        ),
        # Contexto estrategico
        sa.Column(
            "is_break_point",
            sa.Boolean,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_set_point",
            sa.Boolean,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_match_point",
            sa.Boolean,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_game_point",
            sa.Boolean,
            server_default=sa.text("false"),
        ),
        # Timing
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "video_timestamp",
            sa.Float,
            nullable=True,
            comment="Timestamp no video em segundos",
        ),
        # Dados adicionais
        sa.Column(
            "court_position_data",
            JSONB,
            nullable=True,
            comment="Posicoes dos jogadores durante o ponto",
        ),
        sa.Column(
            "ball_trajectory_data",
            JSONB,
            nullable=True,
            comment="Dados de trajetoria da bola",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_point_history_match_id", "point_history", ["match_id"]
    )
    op.create_index(
        "ix_point_history_outcome", "point_history", ["outcome"]
    )
    op.create_index(
        "ix_point_history_server_player_id",
        "point_history",
        ["server_player_id"],
    )
    op.create_index(
        "ix_point_history_point_winner_id",
        "point_history",
        ["point_winner_id"],
    )
    op.create_index(
        "ix_point_history_match_set_game",
        "point_history",
        ["match_id", "set_number", "game_number"],
    )
    op.create_index(
        "ix_point_history_break_point",
        "point_history",
        ["is_break_point"],
    )


def downgrade() -> None:
    """Remover tabelas e enums."""
    # Drop tabelas na ordem inversa (por causa das FKs)
    op.drop_table("point_history")
    op.drop_table("game_events")
    op.drop_table("training_sessions")
    op.drop_table("drill_types")

    # Drop enums
    point_outcome_enum.drop(op.get_bind(), checkfirst=True)
    event_type_enum.drop(op.get_bind(), checkfirst=True)
    session_status_enum.drop(op.get_bind(), checkfirst=True)
    session_type_enum.drop(op.get_bind(), checkfirst=True)
    drill_difficulty_enum.drop(op.get_bind(), checkfirst=True)
    drill_category_enum.drop(op.get_bind(), checkfirst=True)
