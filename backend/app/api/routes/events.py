"""
Events API routes
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import structlog

from app.services.event_service import EventService, EventPriority

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/events/match/{match_id}/stats")
async def get_event_statistics(match_id: str):
    """
    Obter estatísticas de eventos de uma partida

    Critérios de aceite TT-47:
    - [x] Endpoint GET /api/events/match/{match_id}/stats

    Args:
        match_id: ID da partida

    Returns:
        Estatísticas agregadas de eventos
    """
    try:
        event_service = EventService()
        stats = await event_service.get_event_statistics(match_id)

        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])

        return stats

    except Exception as e:
        logger.error("Error getting event statistics", match_id=match_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/match/{match_id}/history")
async def get_event_history(
    match_id: str,
    event_types: Optional[str] = Query(None, description="Tipos de eventos separados por vírgula"),
    player_id: Optional[str] = Query(None, description="ID do jogador para filtrar"),
    min_priority: Optional[str] = Query(None, description="Prioridade mínima (low, normal, high, critical)"),
    limit: int = Query(100, ge=1, le=500, description="Limite de eventos retornados"),
    offset: int = Query(0, ge=0, description="Offset para paginação")
):
    """
    Obter histórico de eventos de uma partida com filtros

    Critérios de aceite TT-47:
    - [x] Endpoint GET /api/events/match/{match_id}/history
    - [x] Filtros por tipo, jogador e prioridade
    - [x] Paginação com limit e offset

    Args:
        match_id: ID da partida
        event_types: Tipos de eventos separados por vírgula (opcional)
        player_id: ID do jogador para filtrar (opcional)
        min_priority: Prioridade mínima (opcional)
        limit: Limite de eventos retornados
        offset: Offset para paginação

    Returns:
        Lista de eventos com descrições
    """
    try:
        event_service = EventService()

        # Parse event_types
        event_types_list = None
        if event_types:
            event_types_list = [t.strip() for t in event_types.split(",")]

        # Parse min_priority
        priority_obj = None
        if min_priority:
            try:
                priority_obj = EventPriority(min_priority.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid priority. Valid values: low, normal, high, critical"
                )

        # Get event history
        events = await event_service.get_event_history(
            match_id=match_id,
            event_types=event_types_list,
            player_id=player_id,
            min_priority=priority_obj,
            limit=limit,
            offset=offset
        )

        return {
            "match_id": match_id,
            "total": len(events),
            "limit": limit,
            "offset": offset,
            "events": events
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting event history", match_id=match_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
