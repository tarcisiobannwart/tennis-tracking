"""Adicionar tabela notifications para sistema de notificacoes

Revision ID: 0008_add_notifications
Revises: 0007_add_tournaments
Create Date: 2026-02-08

Migration: Cria tabela notifications com indices para user_id, created_at, is_read e notification_type.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "0008_add_notifications"
down_revision: Union[str, None] = "0007_add_tournaments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar enum via raw SQL
    op.execute("CREATE TYPE notification_type AS ENUM ('match_result', 'friendship', 'game_scheduled', 'ranking_round', 'tournament', 'system')")

    # Criar tabela sem coluna enum
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("sender_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reference_id", UUID(as_uuid=True), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("is_read", sa.Boolean, default=False, nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Adicionar coluna enum via ALTER TABLE
    op.execute("ALTER TABLE notifications ADD COLUMN notification_type notification_type NOT NULL DEFAULT 'system'")

    # Criar indices
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_sender_id", "notifications", ["sender_id"])
    op.create_index("ix_notifications_reference_id", "notifications", ["reference_id"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_index("ix_notifications_user_created", "notifications", ["user_id", "created_at"])
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "is_read"])
    op.create_index("ix_notifications_type", "notifications", ["notification_type"])
    op.create_index("ix_notifications_reference", "notifications", ["reference_id", "reference_type"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.execute("DROP TYPE IF EXISTS notification_type")
