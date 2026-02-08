"""
Match History API routes - TT-135
Lista historico de partidas com placares detalhados, filtros e paginacao
"""

import uuid
from typing import Optional
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.match_history_service import MatchHistoryService

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/")
async def list_match_history(
    match_type: Optional[str] = Query(None, description="Filtro por tipo: ranking, amistoso, torneio"),
    opponent_name: Optional[str] = Query(None, description="Filtro por nome do oponente"),
    surface: Optional[str] = Query(None, description="Filtro por superficie: clay, grass, hard, carpet"),
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Numero de registros a pular"),
    limit: int = Query(20, ge=1, le=100, description="Numero maximo de registros"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista historico de partidas do usuario com filtros e paginacao.

    Retorna partidas completas com:
    - Data e local
    - Oponente
    - Placar por sets
    - Tipo de partida (ranking/amistoso/torneio)
    - Superficie da quadra
    """
    try:
        user_id = uuid.UUID(str(current_user.id))

        # Parse dates se fornecidas
        parsed_start_date = None
        parsed_end_date = None

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de start_date invalido. Use YYYY-MM-DD")

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de end_date invalido. Use YYYY-MM-DD")

        service = MatchHistoryService()
        result = await service.list_matches(
            db=db,
            user_id=user_id,
            match_type=match_type,
            opponent_name=opponent_name,
            surface=surface,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            skip=skip,
            limit=limit,
        )

        logger.info(
            "Match history retrieved",
            user_id=str(user_id),
            total=result["total"],
            filters={
                "match_type": match_type,
                "opponent_name": opponent_name,
                "surface": surface,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error listing match history", error=str(e), user_id=str(user_id))
        raise HTTPException(status_code=500, detail=f"Erro ao listar historico de partidas: {str(e)}")


@router.get("/{match_id}/detail")
async def get_match_detail(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna detalhes completos de uma partida especifica.

    Inclui:
    - Informacoes basicas (data, local, tipo)
    - Placar detalhado por sets e games
    - Informacoes dos jogadores
    - Estatisticas basicas se disponiveis
    """
    try:
        user_id = uuid.UUID(str(current_user.id))
        match_uuid = uuid.UUID(match_id)

        service = MatchHistoryService()
        match_detail = await service.get_match_detail(
            db=db,
            match_id=match_uuid,
            user_id=user_id,
        )

        if not match_detail:
            raise HTTPException(status_code=404, detail="Partida nao encontrada ou acesso negado")

        logger.info("Match detail retrieved", match_id=match_id, user_id=str(user_id))

        return match_detail

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de partida invalido")
    except Exception as e:
        logger.error("Error getting match detail", error=str(e), match_id=match_id)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar detalhes da partida: {str(e)}")
