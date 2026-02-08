"""
Videos API routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Body
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
import uuid
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import UserInDB
from app.models.sql.video import Video
from app.services.user_service import user_service
from app.services.video_service import VideoService
from app.core.dependencies import get_plan_limits

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a video for analysis"""
    user_id = str(current_user.id)

    # Check plan limits
    limits = get_plan_limits(current_user)
    videos_limit = limits["videos_per_month"]

    if videos_limit > 0:  # -1 = unlimited
        video_count = await user_service.get_video_count_this_month(user_id)
        if video_count >= videos_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Limite de {videos_limit} videos/mes atingido. Faca upgrade do seu plano."
            )

    # Save video info to database
    video = Video(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        filename=file.filename,
        original_filename=file.filename,
        file_size=file.size or 0,
        mime_type=file.content_type or "video/mp4",
        upload_path=f"/app/uploads/{file.filename}",
        status="uploaded",
    )

    db.add(video)
    await db.flush()

    return {
        "id": str(video.id),
        "filename": file.filename,
        "status": "uploaded",
        "message": "Video enviado com sucesso"
    }


@router.get("/")
async def get_user_videos(
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all videos for current user"""
    user_id = str(current_user.id)

    # Check history limit
    limits = get_plan_limits(current_user)
    history_days = limits["history_days"]

    query = select(Video).where(Video.user_id == uuid.UUID(user_id))

    if history_days > 0:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=history_days)
        query = query.where(Video.uploaded_at >= cutoff)

    query = query.order_by(Video.uploaded_at.desc()).limit(100)

    result = await db.execute(query)
    videos = result.scalars().all()

    formatted = []
    for video in videos:
        formatted.append({
            "_id": str(video.id),
            "userId": str(video.user_id),
            "filename": video.filename,
            "contentType": video.mime_type,
            "size": video.file_size,
            "status": video.status,
            "uploadedAt": video.uploaded_at.isoformat() if video.uploaded_at else None,
        })

    return formatted


@router.get("/{video_id}")
async def get_video(
    video_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get video by ID"""
    query = select(Video).where(
        Video.id == uuid.UUID(video_id),
        Video.user_id == uuid.UUID(str(current_user.id))
    )
    result = await db.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video nao encontrado")

    return {
        "_id": str(video.id),
        "userId": str(video.user_id),
        "filename": video.filename,
        "contentType": video.mime_type,
        "size": video.file_size,
        "status": video.status,
        "uploadedAt": video.uploaded_at.isoformat() if video.uploaded_at else None,
    }


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete video"""
    query = select(Video).where(
        Video.id == uuid.UUID(video_id),
        Video.user_id == uuid.UUID(str(current_user.id))
    )
    result = await db.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video nao encontrado")

    await db.delete(video)

    return {"message": "Video excluido com sucesso"}


class BatchProcessRequest(BaseModel):
    """Request model for batch processing"""
    video_ids: List[str]


@router.post("/batch-process")
async def batch_process_videos(
    request: BatchProcessRequest,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Processa multiplos videos em lote

    Criterios de aceite TT-55:
    - [x] Endpoint POST /videos/batch-process
    - [x] Upload batch funcional
    - [x] Controle de concorrencia

    Args:
        request: Lista de IDs de videos para processar
        current_user: Usuario autenticado

    Returns:
        Informacoes do batch job criado
    """
    try:
        logger.info(
            "Batch processing request",
            user_id=str(current_user.id),
            total_videos=len(request.video_ids)
        )

        # Verify all videos belong to user
        for video_id in request.video_ids:
            query = select(Video).where(
                Video.id == uuid.UUID(video_id),
                Video.user_id == uuid.UUID(str(current_user.id))
            )
            result = await db.execute(query)
            video = result.scalar_one_or_none()
            if not video:
                raise HTTPException(
                    status_code=404,
                    detail=f"Video {video_id} nao encontrado ou nao pertence ao usuario"
                )

        # Create batch processing job
        video_service = VideoService()
        batch_info = await video_service.batch_process(request.video_ids)

        return {
            "message": "Batch processing iniciado com sucesso",
            "batch_info": batch_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating batch processing job", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/tasks")
async def list_analysis_tasks(
    status: Optional[str] = None,
    match_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Lista todas as tarefas de analise de video

    Criterios de aceite TT-55:
    - [x] Endpoint GET /analysis/tasks
    - [x] Listagem com filtros por status
    - [x] Paginacao

    Query Parameters:
    - status: Filtrar por status (pending, processing, completed, failed)
    - match_id: Filtrar por ID da partida
    - skip: Numero de tarefas para pular (paginacao)
    - limit: Numero maximo de tarefas retornadas

    Returns:
        Lista de tarefas de analise
    """
    try:
        logger.info(
            "Listing analysis tasks",
            user_id=str(current_user.id),
            status=status,
            match_id=match_id
        )

        video_service = VideoService()

        tasks = await video_service.list_analysis_tasks(
            skip=skip,
            limit=limit,
            status=status,
            match_id=match_id
        )

        return {
            "total": len(tasks),
            "skip": skip,
            "limit": limit,
            "filters": {
                "status": status,
                "match_id": match_id
            },
            "tasks": tasks
        }

    except Exception as e:
        logger.error("Error listing analysis tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
