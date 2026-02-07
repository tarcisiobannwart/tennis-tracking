"""
Videos API routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Body
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel
import structlog

from app.core.mongodb import get_database
from app.core.auth import get_current_active_user
from app.models.user import UserInDB
from app.services.user_service import user_service
from app.services.video_service import VideoService
from app.core.dependencies import get_plan_limits

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Upload a video for analysis"""
    db = get_database()
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
    video_doc = {
        "userId": user_id,
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
        "message": "Video enviado com sucesso"
    }


@router.get("/")
async def get_user_videos(current_user: UserInDB = Depends(get_current_active_user)):
    """Get all videos for current user"""
    db = get_database()
    user_id = str(current_user.id)

    # Check history limit
    limits = get_plan_limits(current_user)
    history_days = limits["history_days"]

    query = {"userId": user_id}
    if history_days > 0:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=history_days)
        query["uploadedAt"] = {"$gte": cutoff}

    videos = await db.videos.find(query).sort("uploadedAt", -1).to_list(100)

    for video in videos:
        video["_id"] = str(video["_id"])

    return videos


@router.get("/{video_id}")
async def get_video(video_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """Get video by ID"""
    db = get_database()
    video = await db.videos.find_one({
        "_id": ObjectId(video_id),
        "userId": str(current_user.id)
    })

    if not video:
        raise HTTPException(status_code=404, detail="Video nao encontrado")

    video["_id"] = str(video["_id"])
    return video


@router.delete("/{video_id}")
async def delete_video(video_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """Delete video"""
    db = get_database()
    result = await db.videos.delete_one({
        "_id": ObjectId(video_id),
        "userId": str(current_user.id)
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video nao encontrado")

    return {"message": "Video excluido com sucesso"}


class BatchProcessRequest(BaseModel):
    """Request model for batch processing"""
    video_ids: List[str]


@router.post("/batch-process")
async def batch_process_videos(
    request: BatchProcessRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Processa múltiplos vídeos em lote

    Critérios de aceite TT-55:
    - [x] Endpoint POST /videos/batch-process
    - [x] Upload batch funcional
    - [x] Controle de concorrência

    Args:
        request: Lista de IDs de vídeos para processar
        current_user: Usuário autenticado

    Returns:
        Informações do batch job criado
    """
    try:
        logger.info(
            "Batch processing request",
            user_id=str(current_user.id),
            total_videos=len(request.video_ids)
        )

        # Verify all videos belong to user
        db = get_database()
        for video_id in request.video_ids:
            video = await db.videos.find_one({
                "_id": ObjectId(video_id),
                "userId": str(current_user.id)
            })
            if not video:
                raise HTTPException(
                    status_code=404,
                    detail=f"Video {video_id} nao encontrado ou nao pertence ao usuario"
                )

        # Create batch processing job
        video_service = VideoService(db)
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
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Lista todas as tarefas de análise de vídeo

    Critérios de aceite TT-55:
    - [x] Endpoint GET /analysis/tasks
    - [x] Listagem com filtros por status
    - [x] Paginação

    Query Parameters:
    - status: Filtrar por status (pending, processing, completed, failed)
    - match_id: Filtrar por ID da partida
    - skip: Número de tarefas para pular (paginação)
    - limit: Número máximo de tarefas retornadas

    Returns:
        Lista de tarefas de análise
    """
    try:
        logger.info(
            "Listing analysis tasks",
            user_id=str(current_user.id),
            status=status,
            match_id=match_id
        )

        db = get_database()
        video_service = VideoService(db)

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
