"""
Analysis API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
import uuid

from app.core.mongodb import get_database
from app.core.auth import get_current_user

router = APIRouter()


@router.post("/start/{video_id}")
async def start_analysis(
    video_id: str,
    current_user=Depends(get_current_user)
):
    """Start video analysis"""
    db = get_database()

    # Verify video exists and belongs to user
    video = await db.videos.find_one({
        "_id": ObjectId(video_id),
        "userId": str(current_user["_id"])
    })

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Create analysis task
    task = {
        "taskId": str(uuid.uuid4()),
        "videoId": video_id,
        "userId": str(current_user["_id"]),
        "status": "queued",
        "progress": 0,
        "createdAt": datetime.utcnow(),
        "results": {}
    }

    result = await db.analysis_tasks.insert_one(task)

    # TODO: Trigger actual analysis worker

    return {
        "taskId": task["taskId"],
        "status": "queued",
        "message": "Analysis started successfully"
    }


@router.get("/status/{task_id}")
async def get_analysis_status(
    task_id: str,
    current_user=Depends(get_current_user)
):
    """Get analysis task status"""
    db = get_database()

    task = await db.analysis_tasks.find_one({
        "taskId": task_id,
        "userId": str(current_user["_id"])
    })

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "taskId": task["taskId"],
        "status": task["status"],
        "progress": task.get("progress", 0),
        "results": task.get("results", {})
    }


@router.get("/results/{task_id}")
async def get_analysis_results(
    task_id: str,
    current_user=Depends(get_current_user)
):
    """Get analysis results"""
    db = get_database()

    task = await db.analysis_tasks.find_one({
        "taskId": task_id,
        "userId": str(current_user["_id"])
    })

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed. Current status: {task['status']}"
        )

    return task.get("results", {})


@router.get("/history")
async def get_analysis_history(current_user=Depends(get_current_user)):
    """Get user's analysis history"""
    db = get_database()

    tasks = await db.analysis_tasks.find(
        {"userId": str(current_user["_id"])}
    ).sort("createdAt", -1).to_list(50)

    # Convert ObjectId to string and format response
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            "taskId": task["taskId"],
            "videoId": task.get("videoId"),
            "status": task["status"],
            "createdAt": task["createdAt"],
            "completedAt": task.get("completedAt")
        })

    return formatted_tasks