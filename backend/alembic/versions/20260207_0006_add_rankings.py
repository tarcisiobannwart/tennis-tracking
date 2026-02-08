"""Adicionar sistema de rankings com rodadas e classificatoria

Revision ID: 0006_add_rankings
Revises: 0005_add_error_reports
Create Date: 2026-02-07

Migration: Cria tabelas rankings, ranking_participants, ranking_rounds e ranking_matches.
Sistema completo de rankings por local/clube com suporte a diferentes tipos (round_robin, challenge),
rodadas, agendamento de jogos e tabelas classificatorias.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "0006_add_rankings"
down_revision: Union[str, None] = "0005_add_error_reports"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar enums
    ranking_type_enum = sa.Enum("round_robin", "challenge", name="ranking_type_enum")
    ranking_type_enum.create(op.get_bind(), checkfirst=True)

    ranking_status_enum = sa.Enum(
        "active", "inactive", "completed",
        name="ranking_status_enum",
    )
    ranking_status_enum.create(op.get_bind(), checkfirst=True)

    # Criar tabela rankings
    op.create_table(
        "rankings",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("ranking_type", sa.String(20), nullable=False, server_default="round_robin"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("organization_id", sa.String, sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("venue", sa.String(200), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("scoring_config", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_round", sa.Integer, default=1, nullable=False),
        sa.Column("total_rounds", sa.Integer, nullable=True),
        sa.Column("is_public", sa.Boolean, default=True, nullable=False),
        sa.Column("allow_self_scheduling", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.Column("created_by", sa.String, sa.ForeignKey("users.id"), nullable=True),
    )

    # Criar tabela ranking_participants
    op.create_table(
        "ranking_participants",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("ranking_id", sa.String, sa.ForeignKey("rankings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("position", sa.Integer, nullable=True),
        sa.Column("previous_position", sa.Integer, nullable=True),
        sa.Column("points", sa.Float, default=0.0, nullable=False),
        sa.Column("matches_played", sa.Integer, default=0, nullable=False),
        sa.Column("matches_won", sa.Integer, default=0, nullable=False),
        sa.Column("matches_lost", sa.Integer, default=0, nullable=False),
        sa.Column("matches_drawn", sa.Integer, default=0, nullable=False),
        sa.Column("sets_won", sa.Integer, default=0, nullable=False),
        sa.Column("sets_lost", sa.Integer, default=0, nullable=False),
        sa.Column("games_won", sa.Integer, default=0, nullable=False),
        sa.Column("games_lost", sa.Integer, default=0, nullable=False),
        sa.Column("position_history", JSONB, default=[], nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )

    # Criar tabela ranking_rounds
    op.create_table(
        "ranking_rounds",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("ranking_id", sa.String, sa.ForeignKey("rankings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("round_number", sa.Integer, nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_completed", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )

    # Criar tabela ranking_matches
    op.create_table(
        "ranking_matches",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("ranking_id", sa.String, sa.ForeignKey("rankings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("round_id", sa.String, sa.ForeignKey("ranking_rounds.id", ondelete="CASCADE"), nullable=True),
        sa.Column("match_id", sa.String, sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("player1_id", sa.String, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("player2_id", sa.String, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("player1_score", sa.String(50), nullable=True),
        sa.Column("player2_score", sa.String(50), nullable=True),
        sa.Column("winner_id", sa.String, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("player1_points", sa.Float, default=0.0, nullable=False),
        sa.Column("player2_points", sa.Float, default=0.0, nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), default="scheduled", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )

    # Criar índices
    op.create_index("ix_rankings_status", "rankings", ["status"])
    op.create_index("ix_rankings_ranking_type", "rankings", ["ranking_type"])
    op.create_index("ix_rankings_organization_id", "rankings", ["organization_id"])
    op.create_index("ix_rankings_created_by", "rankings", ["created_by"])
    op.create_index("ix_rankings_created_at", "rankings", ["created_at"])

    op.create_index("ix_ranking_participants_ranking_id", "ranking_participants", ["ranking_id"])
    op.create_index("ix_ranking_participants_user_id", "ranking_participants", ["user_id"])
    op.create_index("ix_ranking_participants_position", "ranking_participants", ["position"])
    op.create_index("ix_ranking_participants_ranking_user", "ranking_participants", ["ranking_id", "user_id"], unique=True)

    op.create_index("ix_ranking_rounds_ranking_id", "ranking_rounds", ["ranking_id"])
    op.create_index("ix_ranking_rounds_round_number", "ranking_rounds", ["round_number"])
    op.create_index("ix_ranking_rounds_ranking_round", "ranking_rounds", ["ranking_id", "round_number"], unique=True)

    op.create_index("ix_ranking_matches_ranking_id", "ranking_matches", ["ranking_id"])
    op.create_index("ix_ranking_matches_round_id", "ranking_matches", ["round_id"])
    op.create_index("ix_ranking_matches_player1_id", "ranking_matches", ["player1_id"])
    op.create_index("ix_ranking_matches_player2_id", "ranking_matches", ["player2_id"])
    op.create_index("ix_ranking_matches_status", "ranking_matches", ["status"])
    op.create_index("ix_ranking_matches_scheduled_at", "ranking_matches", ["scheduled_at"])


def downgrade() -> None:
    # Remover índices
    op.drop_index("ix_ranking_matches_scheduled_at", "ranking_matches")
    op.drop_index("ix_ranking_matches_status", "ranking_matches")
    op.drop_index("ix_ranking_matches_player2_id", "ranking_matches")
    op.drop_index("ix_ranking_matches_player1_id", "ranking_matches")
    op.drop_index("ix_ranking_matches_round_id", "ranking_matches")
    op.drop_index("ix_ranking_matches_ranking_id", "ranking_matches")

    op.drop_index("ix_ranking_rounds_ranking_round", "ranking_rounds")
    op.drop_index("ix_ranking_rounds_round_number", "ranking_rounds")
    op.drop_index("ix_ranking_rounds_ranking_id", "ranking_rounds")

    op.drop_index("ix_ranking_participants_ranking_user", "ranking_participants")
    op.drop_index("ix_ranking_participants_position", "ranking_participants")
    op.drop_index("ix_ranking_participants_user_id", "ranking_participants")
    op.drop_index("ix_ranking_participants_ranking_id", "ranking_participants")

    op.drop_index("ix_rankings_created_at", "rankings")
    op.drop_index("ix_rankings_created_by", "rankings")
    op.drop_index("ix_rankings_organization_id", "rankings")
    op.drop_index("ix_rankings_ranking_type", "rankings")
    op.drop_index("ix_rankings_status", "rankings")

    # Remover tabelas
    op.drop_table("ranking_matches")
    op.drop_table("ranking_rounds")
    op.drop_table("ranking_participants")
    op.drop_table("rankings")

    # Remover enums
    sa.Enum(name="ranking_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="ranking_status_enum").drop(op.get_bind(), checkfirst=True)
