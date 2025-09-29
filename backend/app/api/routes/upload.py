"""
Upload API routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import os
import uuid
from datetime import datetime
import aiofiles

from app.core.mongodb import get_database
from app.core.auth import get_current_user
from app.core.config import settings
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

router = APIRouter()

# Diretório para uploads
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extensões permitidas
ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Simple auth for development
security = HTTPBearer()

async def get_test_user(token_data = Depends(security)):
    """Simple authentication for development"""
    try:
        # Try to decode test token first
        payload = jwt.decode(token_data.credentials, "test-secret-key", algorithms=["HS256"])
        return {
            "_id": payload.get("sub"),
            "email": payload.get("sub"),
            "name": payload.get("name", "Test User")
        }
    except JWTError:
        # Fallback to main auth system
        try:
            return await get_current_user(token_data.credentials)
        except:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user=Depends(get_test_user)
):
    """Upload video for analysis"""

    # Valida extensão do arquivo
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    # Gera nome único para o arquivo
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    # Salva arquivo
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()

            # Verifica tamanho do arquivo
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )

            await f.write(content)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Salva informações no banco
    db = get_database()
    video_doc = {
        "videoId": file_id,
        "userId": str(current_user["_id"]),
        "fileName": file.filename,
        "filePath": file_path,
        "fileSize": len(content),
        "title": title or file.filename,
        "description": description or "",
        "status": "uploaded",
        "uploadedAt": datetime.utcnow(),
        "analysisStatus": "pending",
        "metadata": {
            "duration": None,
            "width": None,
            "height": None,
            "fps": None
        }
    }

    result = await db.videos.insert_one(video_doc)

    return {
        "videoId": file_id,
        "message": "Video uploaded successfully",
        "fileName": file.filename,
        "fileSize": len(content),
        "status": "uploaded"
    }


@router.get("/status/{video_id}")
async def get_upload_status(
    video_id: str,
    current_user=Depends(get_test_user)
):
    """Get upload status"""
    db = get_database()

    video = await db.videos.find_one({
        "videoId": video_id,
        "userId": str(current_user["_id"])
    })

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "videoId": video["videoId"],
        "status": video["status"],
        "fileName": video["fileName"],
        "uploadedAt": video["uploadedAt"],
        "analysisStatus": video.get("analysisStatus", "pending")
    }


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    current_user=Depends(get_test_user)
):
    """Delete uploaded video"""
    db = get_database()

    video = await db.videos.find_one({
        "videoId": video_id,
        "userId": str(current_user["_id"])
    })

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Remove arquivo físico
    if os.path.exists(video["filePath"]):
        try:
            os.remove(video["filePath"])
        except Exception as e:
            print(f"Error removing file: {e}")

    # Remove do banco
    await db.videos.delete_one({"videoId": video_id})

    return {"message": "Video deleted successfully"}