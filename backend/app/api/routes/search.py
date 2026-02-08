"""
Search API routes.

Implementado para TT-138: Busca global de jogadores, locais, rankings e torneios.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.search_service import SearchService
from app.schemas.search import SearchResponse

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", response_model=SearchResponse)
async def search_global(
    q: str = Query(..., min_length=2, description="Termo de busca (minimo 2 caracteres)"),
    limit: int = Query(5, ge=1, le=10, description="Limite de resultados por categoria"),
    db: AsyncSession = Depends(get_db),
):
    """
    Busca global unificada em jogadores, locais, rankings e torneios.

    Args:
        q: Termo de busca (minimo 2 caracteres)
        limit: Limite de resultados por categoria (1-10, default: 5)
        db: Sessao do banco de dados

    Returns:
        Resultados agrupados por categoria
    """
    try:
        results = await SearchService.search_all(
            db=db,
            query=q,
            limit=limit,
        )

        return SearchResponse(**results)

    except Exception as e:
        logger.error("Erro ao realizar busca global", error=str(e), query=q)
        raise HTTPException(status_code=500, detail="Erro ao realizar busca")
