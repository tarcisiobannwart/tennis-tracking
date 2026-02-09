"""Adicionar tabelas feed_posts, feed_reactions, feed_comments para social feed

Revision ID: 0010_add_social_feed
Revises: 0009_add_match_scores
Create Date: 2026-02-08

Migration: Cria tabelas de social feed (TT-130) com posts, reacoes e comentarios.
Enums post_type e reaction_type criados via raw SQL + ALTER TABLE para evitar
conflito com SQLAlchemy model metadata.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "0010_add_social_feed"
down_revision: Union[str, None] = "0009_add_match_scores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar enums via raw SQL
    op.execute("CREATE TYPE post_type AS ENUM ('text', 'match_result', 'photo', 'text_photo')")
    op.execute("CREATE TYPE reaction_type AS ENUM ('like', 'cheer')")

    # --- Tabela feed_posts (sem coluna post_type - adicionada via ALTER TABLE) ---
    op.create_table(
        "feed_posts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("match_id", UUID(as_uuid=True), nullable=True),
        sa.Column("likes_count", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("cheers_count", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("comments_count", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("shares_count", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("is_public", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Adicionar coluna enum via ALTER TABLE
    op.execute("ALTER TABLE feed_posts ADD COLUMN post_type post_type NOT NULL DEFAULT 'text'")

    # Indices feed_posts
    op.create_index("ix_feed_posts_user_id", "feed_posts", ["user_id"])
    op.create_index("ix_feed_posts_match_id", "feed_posts", ["match_id"])
    op.create_index("ix_feed_posts_created_at", "feed_posts", ["created_at"])
    op.create_index("ix_feed_posts_user_created", "feed_posts", ["user_id", "created_at"])
    op.create_index("ix_feed_posts_type_created", "feed_posts", ["post_type", "created_at"])
    op.create_index("ix_feed_posts_public_created", "feed_posts", ["is_public", "created_at"])

    # --- Tabela feed_reactions (sem coluna reaction_type - adicionada via ALTER TABLE) ---
    op.create_table(
        "feed_reactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("post_id", UUID(as_uuid=True), sa.ForeignKey("feed_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Adicionar coluna enum via ALTER TABLE
    op.execute("ALTER TABLE feed_reactions ADD COLUMN reaction_type reaction_type NOT NULL DEFAULT 'like'")

    # Indices feed_reactions
    op.create_index("ix_feed_reactions_post_id", "feed_reactions", ["post_id"])
    op.create_index("ix_feed_reactions_user_id", "feed_reactions", ["user_id"])
    op.create_index("ix_feed_reactions_post_user", "feed_reactions", ["post_id", "user_id"], unique=True)
    op.create_index("ix_feed_reactions_user", "feed_reactions", ["user_id"])

    # --- Tabela feed_comments ---
    op.create_table(
        "feed_comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("post_id", UUID(as_uuid=True), sa.ForeignKey("feed_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Indices feed_comments
    op.create_index("ix_feed_comments_post_id", "feed_comments", ["post_id"])
    op.create_index("ix_feed_comments_user_id", "feed_comments", ["user_id"])
    op.create_index("ix_feed_comments_post_created", "feed_comments", ["post_id", "created_at"])
    op.create_index("ix_feed_comments_user", "feed_comments", ["user_id"])


def downgrade() -> None:
    op.drop_table("feed_comments")
    op.drop_table("feed_reactions")
    op.drop_table("feed_posts")
    op.execute("DROP TYPE IF EXISTS reaction_type")
    op.execute("DROP TYPE IF EXISTS post_type")
