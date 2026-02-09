"""Criar tabelas players, matches, sets, games e points

Revision ID: 0002_match_tables
Revises: 0002_create_core_tables
Create Date: 2026-02-07

Tabelas core do sistema de partidas de tenis.
Todas usam String como PK (uuid gerado no app).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002_match_tables"
down_revision: Union[str, None] = "0002_create_core_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Criar tabelas players, matches, sets, games, points."""

    # ── players ──────────────────────────────────────────────
    op.create_table(
        "players",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("country", sa.String(3), nullable=True),
        sa.Column("height", sa.Float, nullable=True),
        sa.Column("weight", sa.Float, nullable=True),
        sa.Column("dominant_hand", sa.String(10), nullable=True),
        sa.Column("ranking", sa.Integer, nullable=True),
        sa.Column("skill_level", sa.String(20), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("profile_image_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_players_name", "players", ["name"])
    op.create_index("ix_players_email", "players", ["email"])

    # ── matches ──────────────────────────────────────────────
    op.create_table(
        "matches",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("match_type", sa.String(20), nullable=False, server_default="singles"),
        sa.Column("surface", sa.String(20), nullable=True),
        sa.Column("tournament_name", sa.String(200), nullable=True),
        sa.Column("round_name", sa.String(50), nullable=True),
        sa.Column("player1_id", sa.String, sa.ForeignKey("players.id"), nullable=False),
        sa.Column("player2_id", sa.String, sa.ForeignKey("players.id"), nullable=False),
        sa.Column("best_of_sets", sa.Integer, server_default="3"),
        sa.Column("tiebreak_at", sa.Integer, server_default="6"),
        sa.Column("player1_sets", sa.Integer, server_default="0"),
        sa.Column("player2_sets", sa.Integer, server_default="0"),
        sa.Column("current_set", sa.Integer, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("video_file_path", sa.String(500), nullable=True),
        sa.Column("analysis_status", sa.String(20), server_default="pending"),
        sa.Column("analysis_progress", sa.Integer, server_default="0"),
        sa.Column("analysis_data", sa.JSON, nullable=True),
        sa.Column("venue", sa.String(200), nullable=True),
        sa.Column("court_number", sa.String(10), nullable=True),
        sa.Column("weather_conditions", sa.JSON, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_public", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_matches_status", "matches", ["status"])
    op.create_index("ix_matches_player1_id", "matches", ["player1_id"])
    op.create_index("ix_matches_player2_id", "matches", ["player2_id"])

    # ── sets ─────────────────────────────────────────────────
    op.create_table(
        "sets",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("match_id", sa.String, sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("set_number", sa.Integer, nullable=False),
        sa.Column("player1_games", sa.Integer, server_default="0"),
        sa.Column("player2_games", sa.Integer, server_default="0"),
        sa.Column("player1_tiebreak", sa.Integer, nullable=True),
        sa.Column("player2_tiebreak", sa.Integer, nullable=True),
        sa.Column("is_tiebreak", sa.Boolean, server_default="false"),
        sa.Column("is_completed", sa.Boolean, server_default="false"),
        sa.Column("winner_player_id", sa.String, sa.ForeignKey("players.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("set_stats", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sets_match_id", "sets", ["match_id"])

    # ── games ────────────────────────────────────────────────
    op.create_table(
        "games",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("match_id", sa.String, sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("set_id", sa.String, sa.ForeignKey("sets.id"), nullable=False),
        sa.Column("game_number", sa.Integer, nullable=False),
        sa.Column("player1_score", sa.String(10), server_default="0"),
        sa.Column("player2_score", sa.String(10), server_default="0"),
        sa.Column("server_player_id", sa.String, sa.ForeignKey("players.id"), nullable=False),
        sa.Column("is_completed", sa.Boolean, server_default="false"),
        sa.Column("winner_player_id", sa.String, sa.ForeignKey("players.id"), nullable=True),
        sa.Column("deuce_count", sa.Integer, server_default="0"),
        sa.Column("advantage_player_id", sa.String, sa.ForeignKey("players.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("game_stats", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_games_match_id", "games", ["match_id"])
    op.create_index("ix_games_set_id", "games", ["set_id"])

    # ── points ───────────────────────────────────────────────
    op.create_table(
        "points",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("match_id", sa.String, sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("set_id", sa.String, sa.ForeignKey("sets.id"), nullable=False),
        sa.Column("game_id", sa.String, sa.ForeignKey("games.id"), nullable=False),
        sa.Column("point_number", sa.Integer, nullable=False),
        sa.Column("server_player_id", sa.String, sa.ForeignKey("players.id"), nullable=False),
        sa.Column("winner_player_id", sa.String, sa.ForeignKey("players.id"), nullable=True),
        sa.Column("score_before", sa.JSON, nullable=True),
        sa.Column("outcome", sa.String(20), nullable=True),
        sa.Column("winning_shot", sa.String(20), nullable=True),
        sa.Column("rally_length", sa.Integer, server_default="0"),
        sa.Column("rally_duration", sa.Float, nullable=True),
        sa.Column("serve_speed", sa.Float, nullable=True),
        sa.Column("serve_placement", sa.JSON, nullable=True),
        sa.Column("first_serve_in", sa.Boolean, nullable=True),
        sa.Column("second_serve", sa.Boolean, server_default="false"),
        sa.Column("ball_trajectory", sa.JSON, nullable=True),
        sa.Column("bounce_points", sa.JSON, nullable=True),
        sa.Column("player_positions", sa.JSON, nullable=True),
        sa.Column("video_start_time", sa.Float, nullable=True),
        sa.Column("video_end_time", sa.Float, nullable=True),
        sa.Column("analysis_data", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_points_match_id", "points", ["match_id"])
    op.create_index("ix_points_game_id", "points", ["game_id"])


def downgrade() -> None:
    """Remover tabelas na ordem inversa."""
    op.drop_table("points")
    op.drop_table("games")
    op.drop_table("sets")
    op.drop_table("matches")
    op.drop_table("players")
