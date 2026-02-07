"""
PostgreSQL database connection and configuration using SQLAlchemy 2.0 async.

Este modulo configura a conexao async com PostgreSQL via asyncpg,
fornecendo engine, session factory e classe base para modelos.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


# Async engine para PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe base declarativa para modelos SQLAlchemy 2.0."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency que fornece uma sessao async do banco de dados.

    Uso:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Sessao do banco de dados.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def connect_db() -> None:
    """
    Inicializa a conexao com o banco de dados.
    Chamado durante o startup da aplicacao FastAPI.
    """
    try:
        # Testar conexao
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("Conexao com PostgreSQL estabelecida com sucesso!")
    except Exception as e:
        logger.error(f"Falha ao conectar com PostgreSQL: {e}")
        raise


async def disconnect_db() -> None:
    """
    Fecha a conexao com o banco de dados.
    Chamado durante o shutdown da aplicacao FastAPI.
    """
    await engine.dispose()
    logger.info("Conexao com PostgreSQL encerrada.")
