"""
Game Control API routes
Endpoints para controle de jogo em tempo real
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.game_control_service import GameControlService
from app.schemas.game_control import (
    StartMatchRequest,
    PauseMatchRequest,
    ResumeMatchRequest,
    AddPointRequest,
    GameControlResponse,
    MatchStateResponse,
    GameEventTypeEnum
)

router = APIRouter()


@router.post("/start", response_model=GameControlResponse)
async def start_match(
    request: StartMatchRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia uma partida

    Critérios de aceite TT-29:
    - [x] Endpoint para start_match() com jogador sacador e dados do torneio
    - [x] Validação de estado (não iniciar partida já iniciada)
    - [x] Suporte a formatos best_of_3 e best_of_5
    """
    service = GameControlService(db)

    response = await service.start_match(
        match_id=request.match_id,
        server_player_id=request.server_player_id,
        tournament_data=request.tournament_data
    )

    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)

    return response


@router.post("/pause", response_model=GameControlResponse)
async def pause_match(
    request: PauseMatchRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Pausa uma partida em andamento

    Critérios de aceite TT-29:
    - [x] Endpoint para pause_match() com eventos

    Broadcasts match_paused event via WebSocket to all connected viewers.
    """
    from app.api.websocket.live_stream import broadcast_match_paused
    import structlog

    logger = structlog.get_logger(__name__)
    service = GameControlService(db)

    response = await service.pause_match(
        match_id=request.match_id,
        reason=request.reason
    )

    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)

    # Broadcast match_paused via WebSocket
    try:
        await broadcast_match_paused(request.match_id, request.reason)
    except Exception as ws_error:
        logger.warning("WebSocket broadcast failed", match_id=request.match_id, error=str(ws_error))

    return response


@router.post("/resume", response_model=GameControlResponse)
async def resume_match(
    request: ResumeMatchRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retoma uma partida pausada

    Critérios de aceite TT-29:
    - [x] Endpoint para resume_match() com eventos

    Broadcasts match_resumed event via WebSocket to all connected viewers.
    """
    from app.api.websocket.live_stream import broadcast_match_resumed
    import structlog

    logger = structlog.get_logger(__name__)
    service = GameControlService(db)

    response = await service.resume_match(match_id=request.match_id)

    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)

    # Broadcast match_resumed via WebSocket
    try:
        await broadcast_match_resumed(request.match_id)
    except Exception as ws_error:
        logger.warning("WebSocket broadcast failed", match_id=request.match_id, error=str(ws_error))

    return response


@router.post("/point", response_model=GameControlResponse)
async def add_point(
    request: AddPointRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registra um ponto com metadados

    Critérios de aceite TT-30:
    - [x] Endpoint para add_point() com winner_player_id e point_type
    - [x] Suporte a dados: ball_speed, ball_position, shot_type
    - [x] Validação de estado (partida em andamento, não pausada)
    - [x] Salvar estado antes do ponto para eventos
    """
    service = GameControlService(db)

    response = await service.add_point(
        match_id=request.match_id,
        winner_player_id=request.winner_player_id,
        point_type=request.point_type,
        metadata=request.metadata
    )

    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)

    return response


@router.get("/state/{match_id}", response_model=MatchStateResponse)
async def get_match_state(
    match_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o estado atual da partida
    """
    service = GameControlService(db)

    state = await service.get_match_state(match_id=match_id)

    if not state:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    return state


@router.get("/events/types")
async def get_event_types(current_user=Depends(get_current_user)):
    """
    Retorna os tipos de eventos disponíveis

    Critérios de aceite TT-31:
    - [x] Listar tipos de eventos disponíveis
    """
    return {
        "event_types": [event_type.value for event_type in GameEventTypeEnum],
        "descriptions": {
            "match_started": "Partida iniciada",
            "match_paused": "Partida pausada",
            "match_resumed": "Partida retomada",
            "match_completed": "Partida finalizada",
            "point_scored": "Ponto marcado",
            "game_won": "Game vencido",
            "set_won": "Set vencido",
            "break_point": "Break point",
            "game_point": "Game point",
            "set_point": "Set point",
            "match_point": "Match point",
            "ace": "Ace",
            "winner": "Winner (ponto direto)",
            "double_fault": "Dupla falta"
        }
    }


@router.get("/export/{match_id}")
async def export_match_data(
    match_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Exporta dados completos da partida

    Critérios de aceite TT-33:
    - [x] Endpoint para exportar JSON completo com todas as estatísticas, pontos, eventos, scoring
    """
    service = GameControlService(db)

    export_data = await service.export_match_data(match_id=match_id)

    if not export_data:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    return export_data


@router.get("/statistics/{match_id}")
async def get_match_statistics(
    match_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna estatísticas da partida

    Critérios de aceite TT-33:
    - [x] Endpoint para get_match_statistics() com info, players, score e events_count
    """
    service = GameControlService(db)

    statistics = await service.get_match_statistics(match_id=match_id)

    if not statistics:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    return statistics


@router.get("/events/recent/{match_id}")
async def get_recent_events(
    match_id: str,
    limit: int = 10,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna eventos recentes da partida

    Critérios de aceite TT-33:
    - [x] Endpoint para get_recent_events() com limite configurável
    """
    service = GameControlService(db)

    events = await service.get_recent_events(match_id=match_id, limit=limit)

    return {
        "match_id": match_id,
        "events": events,
        "count": len(events),
        "limit": limit
    }


@router.get("/health")
async def health_check():
    """Health check do módulo de game control"""
    return {
        "status": "healthy",
        "module": "game_control",
        "version": "1.0.0"
    }
