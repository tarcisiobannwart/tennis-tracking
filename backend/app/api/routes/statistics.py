"""
Statistics API routes - TT-133
Dashboard de estatisticas avancadas com graficos e breakdowns
"""

import uuid
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.services.statistics_service import StatisticsService

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/dashboard")
async def get_statistics_dashboard(
    months: int = Query(12, ge=1, le=36, description="Numero de meses para graficos mensais"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna todos os dados do dashboard de estatisticas avancadas.

    Inclui:
    - Resumo geral V/D
    - Breakdown por tipo de jogo
    - Breakdown por tipo de resultado
    - Dados mensais para graficos
    - Estatisticas por superficie
    - Perfil do oponente (lateralidade, faixa etaria)
    - Sequencia de resultados
    """
    try:
        user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))

        service = StatisticsService()
        result = await service.get_dashboard(
            db=db,
            user_id=user_id,
            months=months,
        )

        logger.info(
            "Statistics dashboard retrieved",
            user_id=str(user_id),
            total_matches=result["overall"]["total_matches"],
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting statistics dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatisticas: {str(e)}")


@router.get("/monthly")
async def get_monthly_stats(
    months: int = Query(12, ge=1, le=36, description="Numero de meses"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna jogos mes a mes para grafico de barras.
    """
    try:
        user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))

        service = StatisticsService()
        result = await service.get_monthly(db=db, user_id=user_id, months=months)

        return {"monthly": result}

    except Exception as e:
        logger.error("Error getting monthly stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatisticas mensais: {str(e)}")


@router.get("/breakdown")
async def get_breakdown_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna breakdown por tipo de jogo e tipo de resultado.
    """
    try:
        user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))

        service = StatisticsService()
        result = await service.get_breakdown(db=db, user_id=user_id)

        return result

    except Exception as e:
        logger.error("Error getting breakdown stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar breakdown: {str(e)}")


@router.get("/surface")
async def get_surface_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna estatisticas por tipo de piso (saibro, hard, grama, carpete).
    """
    try:
        user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))

        service = StatisticsService()
        result = await service.get_surface_stats(db=db, user_id=user_id)

        return {"surfaces": result}

    except Exception as e:
        logger.error("Error getting surface stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatisticas por superficie: {str(e)}")


@router.get("/opponent-profile")
async def get_opponent_profile_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna estatisticas vs perfil do oponente.
    Inclui lateralidade (destro/canhoto), backhand (1/2 maos) e faixa etaria.
    """
    try:
        user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))

        service = StatisticsService()
        result = await service.get_opponent_profile(db=db, user_id=user_id)

        return result

    except Exception as e:
        logger.error("Error getting opponent profile stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar perfil do oponente: {str(e)}")


@router.get("/streak")
async def get_result_streak(
    limit: int = Query(30, ge=1, le=100, description="Numero maximo de resultados"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna sequencia de resultados (V/D) para grid visual.
    """
    try:
        user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))

        service = StatisticsService()
        result = await service.get_streak(db=db, user_id=user_id, limit=limit)

        return {"streak": result}

    except Exception as e:
        logger.error("Error getting result streak", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar sequencia de resultados: {str(e)}")
