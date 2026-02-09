"""Adicionar tabela match_scores

Revision ID: 0009_add_match_scores
Revises: 0008_add_notifications
Create Date: 2026-02-08

Tabela match_scores armazena estado completo de pontuacao via JSONB.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = "0009_add_match_scores"
down_revision: Union[str, None] = "0008_add_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "match_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("match_id", sa.String(255), unique=True, nullable=False),
        sa.Column("player1_id", sa.String(255), nullable=False),
        sa.Column("player2_id", sa.String(255), nullable=False),
        sa.Column("format", sa.String(20), nullable=False, server_default="best_of_3"),
        sa.Column("current_server_id", sa.String(255), nullable=False),
        sa.Column("is_complete", sa.Boolean, server_default=sa.text("false")),
        sa.Column("winner_player_id", sa.String(255), nullable=True),
        sa.Column("score_data", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_match_scores_match_id", "match_scores", ["match_id"], unique=True)
    op.create_index("ix_match_scores_is_complete", "match_scores", ["is_complete"])


def downgrade() -> None:
    op.drop_table("match_scores")
