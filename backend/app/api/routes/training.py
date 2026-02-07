"""
Training API routes (MongoDB)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional
import structlog

from app.api.routes.auth import get_current_user
from app.models.training import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingDrillCreate,
    DrillTypeCreate,
)
from app.services.training_service import TrainingService

router = APIRouter()
logger = structlog.get_logger(__name__)
training_service = TrainingService()


# --- Drill Types ---

@router.get("/drills")
async def list_drill_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Get available drill types (seeds default data if empty)"""
    await training_service.seed_drill_types()
    return await training_service.get_drill_types(skip=skip, limit=limit, category=category, difficulty=difficulty)


@router.post("/drills")
async def create_drill_type(
    data: DrillTypeCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new drill type (admin/coach)"""
    return await training_service.create_drill_type(data)


# --- Training Sessions ---

@router.get("/sessions")
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    session_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Get training sessions for the current user"""
    user_id = current_user.get("_id") or current_user.get("id")
    return await training_service.get_sessions(
        user_id=user_id, skip=skip, limit=limit, status=status, session_type=session_type
    )


@router.post("/sessions")
async def create_session(
    data: TrainingSessionCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    return await training_service.create_session(user_id=user_id, data=data)


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    session = await training_service.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")
    return session


@router.put("/sessions/{session_id}")
async def update_session(
    data: TrainingSessionUpdate,
    session_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Update a training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    session = await training_service.update_session(session_id, user_id, data)
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Delete a training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    success = await training_service.delete_session(session_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Training session not found")
    return {"message": "Training session deleted successfully"}


# --- Session lifecycle ---

@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Start a planned training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    session = await training_service.start_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=400, detail="Cannot start session (not found or not planned)")
    return session


@router.post("/sessions/{session_id}/finish")
async def finish_session(
    session_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Finish an in-progress training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    session = await training_service.finish_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=400, detail="Cannot finish session (not found or not in progress)")
    return session


# --- Drills within session ---

@router.post("/sessions/{session_id}/drills")
async def add_drill(
    data: TrainingDrillCreate,
    session_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Add a drill to a training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    session = await training_service.add_drill_to_session(session_id, user_id, data)
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")
    return session


@router.put("/sessions/{session_id}/drills/{drill_id}")
async def update_drill(
    drill_updates: dict,
    session_id: str = Path(...),
    drill_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Update a drill in a training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    session = await training_service.update_drill_in_session(session_id, user_id, drill_id, drill_updates)
    if not session:
        raise HTTPException(status_code=404, detail="Session or drill not found")
    return session


@router.delete("/sessions/{session_id}/drills/{drill_id}")
async def remove_drill(
    session_id: str = Path(...),
    drill_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    """Remove a drill from a training session"""
    user_id = current_user.get("_id") or current_user.get("id")
    session = await training_service.remove_drill_from_session(session_id, user_id, drill_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# --- Progress, Analytics, Calendar, Recommendations ---

@router.get("/progress")
async def get_progress(
    period: str = Query("month"),
    current_user: dict = Depends(get_current_user),
):
    """Get training progress for the current user"""
    user_id = current_user.get("_id") or current_user.get("id")
    return await training_service.get_progress(user_id, period)


@router.get("/analytics")
async def get_analytics(
    session_type: Optional[str] = Query(None),
    period: str = Query("month"),
    current_user: dict = Depends(get_current_user),
):
    """Get training analytics for the current user"""
    user_id = current_user.get("_id") or current_user.get("id")
    return await training_service.get_analytics(user_id, session_type, period)


@router.get("/recommendations")
async def get_recommendations(
    current_user: dict = Depends(get_current_user),
):
    """Get AI-powered training recommendations"""
    user_id = current_user.get("_id") or current_user.get("id")
    return await training_service.get_recommendations(user_id)


@router.get("/calendar")
async def get_calendar(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Get training calendar for the current user"""
    user_id = current_user.get("_id") or current_user.get("id")
    return await training_service.get_calendar(user_id, start_date, end_date)
