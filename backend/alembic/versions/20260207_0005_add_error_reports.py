"""Adicionar tabela error_reports para error reporting automatico

Revision ID: 0005_add_error_reports
Revises: 0004_trajectory_embeddings
Create Date: 2026-02-07

Migration: Cria tabela error_reports com indices para fingerprint, source, status e timestamps.
Suporta deduplicacao via fingerprint SHA256 e integracao com Jira.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = "0005_add_error_reports"
down_revision: Union[str, None] = "0004_trajectory_embeddings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar enums via raw SQL
    op.execute("CREATE TYPE error_source_enum AS ENUM ('frontend', 'backend')")
    op.execute("CREATE TYPE error_report_status_enum AS ENUM ('open', 'reported', 'resolved', 'ignored')")

    # Criar tabela sem colunas enum
    op.create_table(
        "error_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("fingerprint", sa.String(64), unique=True, nullable=False),
        sa.Column("error_type", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("stack_trace", sa.Text, nullable=True),
        sa.Column("jira_issue_key", sa.String(20), nullable=True),
        sa.Column("occurrence_count", sa.Integer, default=1, nullable=False),
        sa.Column("context", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Adicionar colunas enum via ALTER TABLE
    op.execute("ALTER TABLE error_reports ADD COLUMN source error_source_enum NOT NULL")
    op.execute("ALTER TABLE error_reports ADD COLUMN status error_report_status_enum NOT NULL DEFAULT 'open'")

    # Criar indices
    op.create_index("ix_error_reports_fingerprint", "error_reports", ["fingerprint"], unique=True)
    op.create_index("ix_error_reports_source", "error_reports", ["source"])
    op.create_index("ix_error_reports_error_type", "error_reports", ["error_type"])
    op.create_index("ix_error_reports_jira_issue_key", "error_reports", ["jira_issue_key"])
    op.create_index("ix_error_reports_status", "error_reports", ["status"])
    op.create_index("ix_error_reports_source_status", "error_reports", ["source", "status"])
    op.create_index("ix_error_reports_created_at", "error_reports", ["created_at"])
    op.create_index("ix_error_reports_last_seen_at", "error_reports", ["last_seen_at"])


def downgrade() -> None:
    op.drop_table("error_reports")
    op.execute("DROP TYPE IF EXISTS error_source_enum")
    op.execute("DROP TYPE IF EXISTS error_report_status_enum")
