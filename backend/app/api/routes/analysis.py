"""
Analysis API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.sql.video import Video
from app.models.sql.analysis import AnalysisTask

router = APIRouter()


@router.post("/start/{video_id}")
async def start_analysis(
    video_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start video analysis"""

    user_id = str(current_user.id)

    # Verify video exists and belongs to user
    result = await db.execute(
        select(Video).where(
            Video.id == uuid.UUID(video_id),
            Video.user_id == uuid.UUID(user_id)
        )
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Create analysis task
    task = AnalysisTask(
        id=uuid.uuid4(),
        video_id=uuid.UUID(video_id),
        user_id=uuid.UUID(user_id),
        status="pending",
        progress=0,
    )

    db.add(task)
    await db.flush()

    # TODO: Trigger actual analysis worker

    return {
        "taskId": str(task.id),
        "status": "queued",
        "message": "Analysis started successfully"
    }


@router.get("/status/{task_id}")
async def get_analysis_status(
    task_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analysis task status"""

    user_id = str(current_user.id)

    result = await db.execute(
        select(AnalysisTask).where(
            AnalysisTask.id == uuid.UUID(task_id),
            AnalysisTask.user_id == uuid.UUID(user_id)
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "taskId": str(task.id),
        "status": task.status,
        "progress": task.progress or 0,
        "results": task.match_stats or {}
    }


@router.get("/results/{task_id}")
async def get_analysis_results(
    task_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analysis results"""

    user_id = str(current_user.id)

    result = await db.execute(
        select(AnalysisTask).where(
            AnalysisTask.id == uuid.UUID(task_id),
            AnalysisTask.user_id == uuid.UUID(user_id)
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed. Current status: {task.status}"
        )

    return task.match_stats or {}


@router.get("/history")
async def get_analysis_history(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's analysis history"""

    user_id = str(current_user.id)

    result = await db.execute(
        select(AnalysisTask)
        .where(AnalysisTask.user_id == uuid.UUID(user_id))
        .order_by(AnalysisTask.created_at.desc())
        .limit(50)
    )
    tasks = result.scalars().all()

    # Format response
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            "taskId": str(task.id),
            "videoId": str(task.video_id),
            "status": task.status,
            "createdAt": task.created_at,
            "completedAt": task.completed_at
        })

    return formatted_tasks
