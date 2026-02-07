"""Migration inicial - setup PostgreSQL

Revision ID: 0001_initial_setup
Revises:
Create Date: 2026-02-07

Migration vazia para validar que Alembic + PostgreSQL async
estao configurados corretamente.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_setup"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migration inicial vazia - apenas valida configuracao."""
    pass


def downgrade() -> None:
    """Rollback da migration inicial."""
    pass
