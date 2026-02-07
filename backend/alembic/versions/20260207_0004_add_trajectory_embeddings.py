"""Adicionar tabela trajectory_embeddings com pgvector

Revision ID: 0004_trajectory_embeddings
Revises: 0002_training_events_point_history
Create Date: 2026-02-07

Migration TT-126: Adicionar suporte a pgvector para busca por similaridade de trajetórias.
Cria tabela trajectory_embeddings com coluna vector(128) e índice HNSW para busca eficiente.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = "0004_trajectory_embeddings"
down_revision: Union[str, None] = "0002_training_events_point_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Criar extensão pgvector e tabela trajectory_embeddings."""

    # Habilitar extensão pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Criar tabela trajectory_embeddings
    op.create_table(
        "trajectory_embeddings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Referências
        sa.Column("match_id", sa.String(255), nullable=False, index=True),
        sa.Column("point_id", sa.String(255), nullable=True),
        sa.Column("player_id", sa.String(255), nullable=True, index=True),
        # Metadata da trajetória
        sa.Column("shot_type", sa.String(50), nullable=True),
        sa.Column("trajectory_type", sa.String(50), nullable=True),
        sa.Column("num_points", sa.Integer, nullable=False),
        sa.Column("duration_ms", sa.Float, nullable=True),
        # Embedding vector (128 dimensões)
        sa.Column("embedding", sa.TEXT, nullable=False),  # pgvector será aplicado via raw SQL
        # Dados originais
        sa.Column("raw_trajectory", JSONB, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Converter coluna embedding para tipo vector(128)
    op.execute("ALTER TABLE trajectory_embeddings ALTER COLUMN embedding TYPE vector(128) USING embedding::vector(128)")

    # Criar índices compostos
    op.create_index("ix_trajectory_match_player", "trajectory_embeddings", ["match_id", "player_id"])
    op.create_index("ix_trajectory_shot_type", "trajectory_embeddings", ["shot_type"])

    # Criar índice HNSW para busca por similaridade usando cosine distance
    # HNSW é mais rápido que IVFFlat para datasets pequenos/médios
    op.execute("""
        CREATE INDEX ix_trajectory_embedding_hnsw
        ON trajectory_embeddings
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade() -> None:
    """Remover tabela trajectory_embeddings e extensão pgvector."""

    # Remover índices
    op.drop_index("ix_trajectory_embedding_hnsw", "trajectory_embeddings")
    op.drop_index("ix_trajectory_shot_type", "trajectory_embeddings")
    op.drop_index("ix_trajectory_match_player", "trajectory_embeddings")

    # Remover tabela
    op.drop_table("trajectory_embeddings")

    # Remover extensão pgvector (comentado para não afetar outras tabelas que possam usar)
    # op.execute("DROP EXTENSION IF EXISTS vector")
