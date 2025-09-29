"""
Videos API routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from datetime import datetime
from bson import ObjectId

from app.core.mongodb import get_database
from app.core.auth import get_current_user

router = APIRouter()


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload a video for analysis"""
    db = get_database()

    # Save video info to database
    video_doc = {
        "userId": str(current_user["_id"]),
        "filename": file.filename,
        "contentType": file.content_type,
        "size": file.size,
        "status": "uploaded",
        "uploadedAt": datetime.utcnow()
    }

    result = await db.videos.insert_one(video_doc)

    return {
        "id": str(result.inserted_id),
        "filename": file.filename,
        "status": "uploaded",
        "message": "Video uploaded successfully"
    }


@router.get("/")
async def get_user_videos(current_user=Depends(get_current_user)):
    """Get all videos for current user"""
    db = get_database()
    videos = await db.videos.find(
        {"userId": str(current_user["_id"])}
    ).sort("uploadedAt", -1).to_list(100)

    # Convert ObjectId to string
    for video in videos:
        video["_id"] = str(video["_id"])

    return videos


@router.get("/{video_id}")
async def get_video(video_id: str, current_user=Depends(get_current_user)):
    """Get video by ID"""
    db = get_database()
    video = await db.videos.find_one({
        "_id": ObjectId(video_id),
        "userId": str(current_user["_id"])
    })

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video["_id"] = str(video["_id"])
    return video


@router.delete("/{video_id}")
async def delete_video(video_id: str, current_user=Depends(get_current_user)):
    """Delete video"""
    db = get_database()
    result = await db.videos.delete_one({
        "_id": ObjectId(video_id),
        "userId": str(current_user["_id"])
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")

    return {"message": "Video deleted successfully"}