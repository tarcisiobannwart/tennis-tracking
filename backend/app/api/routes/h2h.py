"""
H2H (Head to Head) API routes - TT-134
Endpoints para comparativo H2H entre jogadores
"""

import uuid
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.services.h2h_service import H2HService

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/{player_id}/{opponent_id}")
async def get_h2h(
    player_id: str,
    opponent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna dados completos do H2H entre dois jogadores.

    Inclui:
    - Perfis dos jogadores
    - Placar H2H
    - Tabela comparativa
    - Graficos de sets/games ao longo do tempo
    - Historico de confrontos
    """
    try:
        p_id = uuid.UUID(player_id)
        o_id = uuid.UUID(opponent_id)

        service = H2HService()
        result = await service.get_h2h(db=db, player_id=p_id, opponent_id=o_id)

        if not result:
            raise HTTPException(status_code=404, detail="Jogador ou adversario nao encontrado")

        logger.info(
            "H2H data retrieved",
            player_id=player_id,
            opponent_id=opponent_id,
            total_matches=result["total_matches"],
        )

        return result

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de jogador invalido")
    except Exception as e:
        logger.error("Error getting H2H data", error=str(e), player_id=player_id, opponent_id=opponent_id)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados H2H: {str(e)}")


@router.get("/{player_id}/opponents")
async def get_opponents_list(
    player_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista todos os adversarios do jogador com H2H resumido.

    Retorna lista ordenada por numero de confrontos.
    """
    try:
        p_id = uuid.UUID(player_id)

        service = H2HService()
        result = await service.get_opponents_list(db=db, player_id=p_id)

        logger.info(
            "Opponents list retrieved",
            player_id=player_id,
            total_opponents=len(result),
        )

        return {"opponents": result}

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de jogador invalido")
    except Exception as e:
        logger.error("Error getting opponents list", error=str(e), player_id=player_id)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lista de adversarios: {str(e)}")


@router.get("/{player_id}/{opponent_id}/matches")
async def get_h2h_matches(
    player_id: str,
    opponent_id: str,
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(20, ge=1, le=100, description="Limite de registros"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna historico de confrontos diretos com paginacao.
    """
    try:
        p_id = uuid.UUID(player_id)
        o_id = uuid.UUID(opponent_id)

        service = H2HService()
        result = await service.get_h2h_matches(
            db=db,
            player_id=p_id,
            opponent_id=o_id,
            skip=skip,
            limit=limit,
        )

        return result

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de jogador invalido")
    except Exception as e:
        logger.error("Error getting H2H matches", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar confrontos: {str(e)}")
