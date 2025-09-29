"""
Live Analysis API routes for video processing
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import structlog

from app.core.database import get_db
from app.core.exceptions import VideoProcessingException, InvalidVideoFormatException, FileTooLargeException
from app.schemas.video import (
    VideoUploadResponse,
    VideoAnalysisResponse,
    VideoAnalysisStatus,
    VideoAnalysisOptions
)
from app.services.video_service import VideoService
from app.services.analysis_service import AnalysisService
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/video", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    match_id: Optional[str] = Form(None),
    analysis_options: Optional[str] = Form(None),  # JSON string
    db: AsyncSession = Depends(get_db)
):
    """
    Upload video file for analysis
    """
    logger.info("Uploading video", filename=file.filename, match_id=match_id)

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    allowed_extensions = settings.ALLOWED_VIDEO_EXTENSIONS
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise InvalidVideoFormatException(file.filename.split('.')[-1])

    # Check file size (rough estimate from content-length header)
    if hasattr(file, 'size') and file.size > settings.MAX_FILE_SIZE:
        raise FileTooLargeException(file.size, settings.MAX_FILE_SIZE)

    # Generate task ID
    task_id = str(uuid.uuid4())

    try:
        video_service = VideoService(db)

        # Save uploaded file
        file_path = await video_service.save_uploaded_file(file, task_id)

        # Parse analysis options
        options = VideoAnalysisOptions()
        if analysis_options:
            import json
            options_dict = json.loads(analysis_options)
            options = VideoAnalysisOptions(**options_dict)

        # Create analysis task
        analysis_task = await video_service.create_analysis_task(
            task_id=task_id,
            file_path=file_path,
            match_id=match_id,
            options=options
        )

        # Start background processing
        analysis_service = AnalysisService(db)
        background_tasks.add_task(
            analysis_service.process_video,
            task_id,
            file_path,
            options
        )

        logger.info("Video upload successful", task_id=task_id, file_path=file_path)

        return VideoUploadResponse(
            task_id=task_id,
            upload_url=f"/api/analyze/status/{task_id}",
            expires_at=analysis_task.created_at,
            chunk_size=1024 * 1024
        )

    except Exception as e:
        logger.error("Video upload failed", error=str(e), exc_info=True)
        raise VideoProcessingException(str(e))


@router.get("/status/{task_id}", response_model=VideoAnalysisStatus)
async def get_analysis_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of video analysis task
    """
    logger.info("Checking analysis status", task_id=task_id)

    video_service = VideoService(db)
    status = await video_service.get_analysis_status(task_id)

    if not status:
        raise HTTPException(status_code=404, detail="Analysis task not found")

    return status


@router.get("/result/{task_id}", response_model=VideoAnalysisResponse)
async def get_analysis_result(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get results of completed video analysis
    """
    logger.info("Fetching analysis result", task_id=task_id)

    video_service = VideoService(db)
    result = await video_service.get_analysis_result(task_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    if result.status != "completed":
        raise HTTPException(
            status_code=422,
            detail=f"Analysis not completed. Current status: {result.status}"
        )

    return result


@router.delete("/task/{task_id}")
async def cancel_analysis(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a running video analysis task
    """
    logger.info("Cancelling analysis", task_id=task_id)

    video_service = VideoService(db)
    success = await video_service.cancel_analysis(task_id)

    if not success:
        raise HTTPException(status_code=404, detail="Analysis task not found")

    logger.info("Analysis cancelled", task_id=task_id)
    return {"message": "Analysis task cancelled successfully"}


@router.post("/reprocess/{task_id}")
async def reprocess_video(
    task_id: str,
    background_tasks: BackgroundTasks,
    analysis_options: Optional[VideoAnalysisOptions] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Reprocess a video with different analysis options
    """
    logger.info("Reprocessing video", task_id=task_id)

    video_service = VideoService(db)

    # Get original task
    original_task = await video_service.get_analysis_result(task_id)
    if not original_task:
        raise HTTPException(status_code=404, detail="Original analysis task not found")

    # Generate new task ID
    new_task_id = str(uuid.uuid4())

    try:
        # Create new analysis task with same file
        new_task = await video_service.create_analysis_task(
            task_id=new_task_id,
            file_path=original_task.video_file_path,  # Reuse original file
            match_id=original_task.match_id,
            options=analysis_options or VideoAnalysisOptions()
        )

        # Start background processing
        analysis_service = AnalysisService(db)
        background_tasks.add_task(
            analysis_service.process_video,
            new_task_id,
            original_task.video_file_path,
            analysis_options or VideoAnalysisOptions()
        )

        logger.info("Video reprocessing started", new_task_id=new_task_id)

        return {
            "message": "Video reprocessing started",
            "new_task_id": new_task_id,
            "original_task_id": task_id
        }

    except Exception as e:
        logger.error("Video reprocessing failed", error=str(e), exc_info=True)
        raise VideoProcessingException(str(e))


@router.get("/tasks")
async def list_analysis_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    match_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List video analysis tasks with optional filtering
    """
    logger.info("Listing analysis tasks", skip=skip, limit=limit, status=status)

    video_service = VideoService(db)
    tasks = await video_service.list_analysis_tasks(
        skip=skip,
        limit=limit,
        status=status,
        match_id=match_id
    )

    return tasks


@router.post("/batch")
async def batch_process_videos(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    match_ids: Optional[list[str]] = Form(None),
    analysis_options: Optional[str] = Form(None),  # JSON string
    db: AsyncSession = Depends(get_db)
):
    """
    Batch process multiple video files
    """
    logger.info("Starting batch video processing", file_count=len(files))

    if len(files) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch")

    # Parse analysis options
    options = VideoAnalysisOptions()
    if analysis_options:
        import json
        options_dict = json.loads(analysis_options)
        options = VideoAnalysisOptions(**options_dict)

    task_ids = []
    video_service = VideoService(db)
    analysis_service = AnalysisService(db)

    for i, file in enumerate(files):
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())

            # Get corresponding match_id if provided
            match_id = match_ids[i] if match_ids and i < len(match_ids) else None

            # Save uploaded file
            file_path = await video_service.save_uploaded_file(file, task_id)

            # Create analysis task
            await video_service.create_analysis_task(
                task_id=task_id,
                file_path=file_path,
                match_id=match_id,
                options=options
            )

            # Start background processing
            background_tasks.add_task(
                analysis_service.process_video,
                task_id,
                file_path,
                options
            )

            task_ids.append(task_id)

        except Exception as e:
            logger.error("Failed to process file in batch", filename=file.filename, error=str(e))
            # Continue with other files

    logger.info("Batch processing started", task_count=len(task_ids))

    return {
        "message": f"Batch processing started for {len(task_ids)} videos",
        "task_ids": task_ids,
        "failed_count": len(files) - len(task_ids)
    }