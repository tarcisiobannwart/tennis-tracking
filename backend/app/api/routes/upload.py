"""
Upload API routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import os
import uuid
from datetime import datetime
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.config import settings
from app.models.sql.video import Video
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

router = APIRouter()

# Diretorio para uploads
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extensoes permitidas
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


def _get_user_id(current_user) -> str:
    """Extract user ID from either dict (test user) or UserInDB object"""
    if isinstance(current_user, dict):
        return current_user["_id"]
    return str(current_user.id)


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user=Depends(get_test_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload video for analysis"""

    # Valida extensao do arquivo
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    # Gera nome unico para o arquivo
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
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Salva informacoes no banco
    user_id = _get_user_id(current_user)

    video = Video(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id),
        filename=file_name,
        original_filename=file.filename,
        file_size=len(content),
        mime_type=file.content_type or "video/mp4",
        upload_path=file_path,
        status="uploaded",
        description=description or "",
        metadata_={
            "title": title or file.filename,
            "duration": None,
            "width": None,
            "height": None,
            "fps": None,
            "analysisStatus": "pending"
        }
    )

    db.add(video)
    await db.flush()

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
    current_user=Depends(get_test_user),
    db: AsyncSession = Depends(get_db)
):
    """Get upload status"""

    user_id = _get_user_id(current_user)

    # Search by filename pattern (video_id is the UUID prefix of the filename)
    result = await db.execute(
        select(Video).where(
            Video.filename.like(f"{video_id}%"),
            Video.user_id == (uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
        )
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    metadata = video.metadata_ or {}
    return {
        "videoId": video_id,
        "status": video.status,
        "fileName": video.original_filename,
        "uploadedAt": video.uploaded_at,
        "analysisStatus": metadata.get("analysisStatus", "pending")
    }


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    current_user=Depends(get_test_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete uploaded video"""

    user_id = _get_user_id(current_user)

    result = await db.execute(
        select(Video).where(
            Video.filename.like(f"{video_id}%"),
            Video.user_id == (uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
        )
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Remove arquivo fisico
    if video.upload_path and os.path.exists(video.upload_path):
        try:
            os.remove(video.upload_path)
        except Exception as e:
            print(f"Error removing file: {e}")

    # Remove do banco
    await db.delete(video)

    return {"message": "Video deleted successfully"}
