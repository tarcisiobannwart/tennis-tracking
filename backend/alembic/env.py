"""
Alembic environment configuration para PostgreSQL async.

Utiliza asyncpg como driver async e carrega a DATABASE_URL
do config.py da aplicacao quando disponivel.
"""

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models here
from app.core.database import Base

# Importar modelos SQLAlchemy para autogenerate
from app.models.sql import (  # noqa: F401
    User,
    Organization,
    OrganizationInvite,
    SubscriptionEvent,
    ActivityLog,
    # TT-120: modelos de video, streams, analysis e player_stats
    Video,
    Stream,
    AnalysisTask,
    PlayerStats,
)

# TT-121: modelos de training, game_events e point_history
from app.models.training import DrillType, TrainingSession  # noqa: F401
from app.models.event import GameEvent  # noqa: F401
from app.models.point_history import PointHistory  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Sobrescrever sqlalchemy.url com DATABASE_URL do config da aplicacao
try:
    from app.core.config import settings
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
except ImportError:
    pass  # Usa o valor do alembic.ini como fallback

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode com engine async.

    Cria um AsyncEngine e executa as migrations dentro
    de uma conexao async.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()