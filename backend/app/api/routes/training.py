"""
Training API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import PlayerNotFoundException
from app.schemas.training import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingSessionResponse,
    DrillTypeResponse,
    TrainingDrillCreate,
    TrainingDrillResponse
)
from app.services.training_service import TrainingService
from app.services.player_service import PlayerService
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/drills", response_model=List[DrillTypeResponse])
async def list_drill_types(
    skip: int = Query(0, ge=0, description="Number of drills to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of drills to return"),
    category: Optional[str] = Query(None, description="Filter by drill category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of available drill types
    """
    logger.info("Fetching drill types", category=category, difficulty=difficulty)

    training_service = TrainingService(db)
    drills = await training_service.get_drill_types(
        skip=skip,
        limit=limit,
        category=category,
        difficulty=difficulty
    )

    return drills


@router.post("/sessions", response_model=TrainingSessionResponse)
async def create_training_session(
    session_data: TrainingSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new training session
    """
    logger.info("Creating training session", player_id=session_data.player_id, title=session_data.title)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(session_data.player_id)
    if not player:
        raise PlayerNotFoundException(session_data.player_id)

    training_service = TrainingService(db)
    session = await training_service.create_training_session(session_data)

    logger.info("Training session created", session_id=session.id)
    return session


@router.get("/sessions", response_model=List[TrainingSessionResponse])
async def list_training_sessions(
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of sessions to return"),
    player_id: Optional[str] = Query(None, description="Filter by player ID"),
    status: Optional[str] = Query(None, description="Filter by session status"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of training sessions with optional filtering
    """
    logger.info("Fetching training sessions", player_id=player_id, status=status)

    training_service = TrainingService(db)
    sessions = await training_service.get_training_sessions(
        skip=skip,
        limit=limit,
        player_id=player_id,
        status=status,
        session_type=session_type
    )

    return sessions


@router.get("/sessions/{session_id}", response_model=TrainingSessionResponse)
async def get_training_session(
    session_id: str = Path(..., description="Training session ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific training session by ID
    """
    logger.info("Fetching training session", session_id=session_id)

    training_service = TrainingService(db)
    session = await training_service.get_training_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")

    return session


@router.put("/sessions/{session_id}", response_model=TrainingSessionResponse)
async def update_training_session(
    session_id: str = Path(..., description="Training session ID"),
    session_data: TrainingSessionUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a training session
    """
    logger.info("Updating training session", session_id=session_id)

    training_service = TrainingService(db)
    session = await training_service.update_training_session(session_id, session_data)

    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")

    logger.info("Training session updated", session_id=session_id)
    return session


@router.delete("/sessions/{session_id}")
async def delete_training_session(
    session_id: str = Path(..., description="Training session ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a training session
    """
    logger.info("Deleting training session", session_id=session_id)

    training_service = TrainingService(db)
    success = await training_service.delete_training_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Training session not found")

    logger.info("Training session deleted", session_id=session_id)
    return {"message": "Training session deleted successfully"}


@router.post("/sessions/{session_id}/drills", response_model=TrainingDrillResponse)
async def add_drill_to_session(
    session_id: str = Path(..., description="Training session ID"),
    drill_data: TrainingDrillCreate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Add a drill to a training session
    """
    logger.info("Adding drill to session", session_id=session_id, drill_type_id=drill_data.drill_type_id)

    training_service = TrainingService(db)
    drill = await training_service.add_drill_to_session(session_id, drill_data)

    if not drill:
        raise HTTPException(status_code=404, detail="Training session not found")

    logger.info("Drill added to session", drill_id=drill.id)
    return drill


@router.put("/drills/{drill_id}", response_model=TrainingDrillResponse)
async def update_training_drill(
    drill_id: str = Path(..., description="Training drill ID"),
    drill_updates: dict = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a training drill
    """
    logger.info("Updating training drill", drill_id=drill_id)

    training_service = TrainingService(db)
    drill = await training_service.update_training_drill(drill_id, drill_updates)

    if not drill:
        raise HTTPException(status_code=404, detail="Training drill not found")

    logger.info("Training drill updated", drill_id=drill_id)
    return drill


@router.post("/sessions/{session_id}/start")
async def start_training_session(
    session_id: str = Path(..., description="Training session ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a scheduled training session
    """
    logger.info("Starting training session", session_id=session_id)

    training_service = TrainingService(db)
    session = await training_service.start_training_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")

    logger.info("Training session started", session_id=session_id)
    return {"message": "Training session started successfully", "session": session}


@router.post("/sessions/{session_id}/finish")
async def finish_training_session(
    session_id: str = Path(..., description="Training session ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Finish a training session in progress
    """
    logger.info("Finishing training session", session_id=session_id)

    training_service = TrainingService(db)
    session = await training_service.finish_training_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")

    logger.info("Training session finished", session_id=session_id)
    return {"message": "Training session finished successfully", "session": session}


@router.get("/progress/{player_id}")
async def get_training_progress(
    player_id: str = Path(..., description="Player ID"),
    period: str = Query("month", description="Time period: week, month, quarter, year"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get training progress for a player
    """
    logger.info("Fetching training progress", player_id=player_id, period=period)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    training_service = TrainingService(db)
    progress = await training_service.get_training_progress(player_id, period)

    return progress


@router.get("/analytics/{player_id}")
async def get_training_analytics(
    player_id: str = Path(..., description="Player ID"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    period: str = Query("month", description="Time period for analysis"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get training analytics for a player
    """
    logger.info("Fetching training analytics", player_id=player_id, period=period)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    training_service = TrainingService(db)
    analytics = await training_service.get_training_analytics(
        player_id, session_type, period
    )

    return analytics


@router.get("/recommendations/{player_id}")
async def get_training_recommendations(
    player_id: str = Path(..., description="Player ID"),
    focus_area: Optional[str] = Query(None, description="Specific area to focus on"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered training recommendations for a player
    """
    logger.info("Generating training recommendations", player_id=player_id, focus_area=focus_area)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    training_service = TrainingService(db)
    recommendations = await training_service.get_training_recommendations(
        player_id, focus_area
    )

    return recommendations


@router.get("/calendar/{player_id}")
async def get_training_calendar(
    player_id: str = Path(..., description="Player ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get training calendar for a player
    """
    logger.info("Fetching training calendar", player_id=player_id)

    # Verify player exists
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise PlayerNotFoundException(player_id)

    training_service = TrainingService(db)
    calendar = await training_service.get_training_calendar(
        player_id, start_date, end_date
    )

    return calendar