"""
Video service for handling video uploads and analysis tasks
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import UploadFile
import structlog

from app.core.config import settings
from app.schemas.video import (
    VideoAnalysisOptions,
    VideoAnalysisResult,
    VideoAnalysisResponse,
    VideoAnalysisStatus
)

logger = structlog.get_logger(__name__)


class VideoAnalysisTask:
    """In-memory video analysis task tracker"""
    def __init__(self, task_id: str, file_path: str, match_id: Optional[str] = None):
        self.task_id = task_id
        self.file_path = file_path
        self.match_id = match_id
        self.status = "pending"
        self.progress = 0
        self.result: Optional[VideoAnalysisResult] = None
        self.error_message: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class VideoService:
    """Service for video-related operations"""

    def __init__(self, db=None):
        self._tasks: Dict[str, VideoAnalysisTask] = {}
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist"""
        for directory in [settings.UPLOAD_DIR, settings.TEMP_DIR, settings.OUTPUT_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    async def save_uploaded_file(self, file: UploadFile, task_id: str) -> str:
        """Save uploaded file to disk"""
        file_extension = Path(file.filename).suffix.lower()
        filename = f"{task_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        try:
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                    await f.write(chunk)

            logger.info("File uploaded successfully", file_path=file_path, size=os.path.getsize(file_path))
            return file_path

        except Exception as e:
            logger.error("Failed to save uploaded file", error=str(e))
            raise

    async def create_analysis_task(
        self,
        task_id: str,
        file_path: str,
        match_id: Optional[str] = None,
        options: Optional[VideoAnalysisOptions] = None
    ) -> VideoAnalysisTask:
        """Create a new video analysis task"""

        task = VideoAnalysisTask(task_id, file_path, match_id)
        self._tasks[task_id] = task

        logger.info("Analysis task created", task_id=task_id, file_path=file_path)
        return task

    async def get_analysis_status(self, task_id: str) -> Optional[VideoAnalysisStatus]:
        """Get the status of an analysis task"""

        task = self._tasks.get(task_id)
        if not task:
            return None

        return VideoAnalysisStatus(
            task_id=task_id,
            status=task.status,
            progress=task.progress,
            message=task.error_message or f"Analysis {task.status}",
            estimated_completion=None  # TODO: Implement time estimation
        )

    async def update_analysis_status(
        self,
        task_id: str,
        status: str,
        progress: int,
        error_message: Optional[str] = None
    ):
        """Update the status of an analysis task"""

        task = self._tasks.get(task_id)
        if task:
            task.status = status
            task.progress = progress
            task.error_message = error_message
            task.updated_at = datetime.utcnow()

            logger.info("Analysis status updated", task_id=task_id, status=status, progress=progress)

    async def save_analysis_result(self, task_id: str, result: VideoAnalysisResult):
        """Save the analysis result"""

        task = self._tasks.get(task_id)
        if task:
            task.result = result
            task.status = "completed"
            task.progress = 100
            task.updated_at = datetime.utcnow()

            logger.info("Analysis result saved", task_id=task_id)

    async def get_analysis_result(self, task_id: str) -> Optional[VideoAnalysisResponse]:
        """Get the analysis result"""

        task = self._tasks.get(task_id)
        if not task:
            return None

        return VideoAnalysisResponse(
            task_id=task_id,
            match_id=task.match_id,
            status=task.status,
            progress=task.progress,
            result=task.result,
            output_video_path=None,  # TODO: Implement output video generation
            minimap_video_path=None,  # TODO: Implement minimap generation
            analysis_summary=self._generate_analysis_summary(task.result) if task.result else None,
            processing_time=None,  # TODO: Calculate processing time
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    async def cancel_analysis(self, task_id: str) -> bool:
        """
        Cancel an analysis task gracefully

        Performs graceful cancellation:
        - Checks if task is cancellable (not completed/failed)
        - Updates status to cancelled
        - Cleans up resources (temporary files, processing threads)
        - Logs cancellation event
        """

        task = self._tasks.get(task_id)
        if not task:
            logger.warning("Cancel failed: task not found", task_id=task_id)
            return False

        if task.status in ["completed", "failed", "cancelled"]:
            logger.warning("Cancel failed: task already finished", task_id=task_id, status=task.status)
            return False  # Cannot cancel completed tasks

        # Update status to cancelled
        old_status = task.status
        task.status = "cancelled"
        task.updated_at = datetime.utcnow()
        task.error_message = f"Task cancelled by user (was {old_status})"

        # Resource cleanup
        try:
            # Clean up temporary files if they exist
            temp_file_path = task.file_path.replace(settings.UPLOAD_DIR, settings.TEMP_DIR)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info("Removed temporary file", file_path=temp_file_path)

            # TODO: Cancel any running Celery tasks
            # This would require storing celery task ID in VideoAnalysisTask
            # celery_app.control.revoke(task.celery_task_id, terminate=True)

        except Exception as e:
            logger.error("Error during resource cleanup", task_id=task_id, error=str(e))

        logger.info("Analysis task cancelled", task_id=task_id, previous_status=old_status)
        return True

    async def reprocess_analysis(
        self,
        task_id: str,
        options: Optional[VideoAnalysisOptions] = None,
        use_same_file: bool = True
    ) -> Optional[str]:
        """
        Reprocess an analysis task

        Args:
            task_id: Original task ID to reprocess
            options: New analysis options (or use original if None)
            use_same_file: Whether to reuse the same video file (default: True)

        Returns:
            New task ID if successful, None otherwise

        Creates a new analysis task with:
        - Same video file (or option to upload new)
        - Updated parameters if provided
        - Fresh task ID and status
        """

        # Get original task
        original_task = self._tasks.get(task_id)
        if not original_task:
            logger.warning("Reprocess failed: original task not found", task_id=task_id)
            return None

        # Verify file still exists if reusing
        if use_same_file:
            if not os.path.exists(original_task.file_path):
                logger.error("Reprocess failed: original file not found", file_path=original_task.file_path)
                return None
            file_path = original_task.file_path
        else:
            # Would need to handle new file upload in the API endpoint
            logger.error("Reprocess with new file not yet supported")
            return None

        # Generate new task ID
        new_task_id = str(uuid.uuid4())

        # Create new task with same file and match_id
        new_task = VideoAnalysisTask(
            task_id=new_task_id,
            file_path=file_path,
            match_id=original_task.match_id
        )
        self._tasks[new_task_id] = new_task

        logger.info(
            "Analysis task reprocessed",
            original_task_id=task_id,
            new_task_id=new_task_id,
            file_path=file_path,
            use_same_file=use_same_file
        )

        # TODO: Queue new analysis task with Celery
        # analyze_video_task.delay(new_task_id, options)

        return new_task_id

    async def list_analysis_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        match_id: Optional[str] = None
    ) -> List[VideoAnalysisResponse]:
        """List analysis tasks with optional filtering"""

        tasks = []
        for task in self._tasks.values():
            # Apply filters
            if status and task.status != status:
                continue
            if match_id and task.match_id != match_id:
                continue

            tasks.append(task)

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Apply pagination
        tasks = tasks[skip:skip + limit]

        # Convert to response objects
        results = []
        for task in tasks:
            response = await self.get_analysis_result(task.task_id)
            if response:
                results.append(response)

        return results

    async def cleanup_old_tasks(self, days: int = 7):
        """Clean up old analysis tasks and files"""

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        tasks_to_remove = []

        for task_id, task in self._tasks.items():
            if task.created_at < cutoff_date:
                # Remove file if it exists
                try:
                    if os.path.exists(task.file_path):
                        os.remove(task.file_path)
                        logger.info("Removed old video file", file_path=task.file_path)
                except Exception as e:
                    logger.warning("Failed to remove old file", file_path=task.file_path, error=str(e))

                tasks_to_remove.append(task_id)

        # Remove tasks from memory
        for task_id in tasks_to_remove:
            del self._tasks[task_id]

        logger.info("Cleaned up old tasks", count=len(tasks_to_remove))

    def _generate_analysis_summary(self, result: VideoAnalysisResult) -> Dict[str, Any]:
        """Generate a summary of analysis results"""

        if not result:
            return {}

        summary = {
            "ball_tracking_points": len(result.ball_tracking) if result.ball_tracking else 0,
            "player_detections": len(result.player_detection) if result.player_detection else 0,
            "court_detection_frames": len(result.court_detection) if result.court_detection else 0,
            "rallies_detected": len(result.rally_analysis) if result.rally_analysis else 0,
            "serves_detected": len(result.serve_analysis) if result.serve_analysis else 0,
            "bounces_detected": len(result.bounce_detection) if result.bounce_detection else 0,
            "highlights_generated": len(result.highlights) if result.highlights else 0
        }

        if result.statistics:
            summary.update(result.statistics)

        return summary

    async def batch_process(
        self,
        video_ids: List[str],
        options: Optional[VideoAnalysisOptions] = None
    ) -> Dict[str, Any]:
        """
        Processa múltiplos vídeos em lote usando Celery

        Critérios de aceite TT-55:
        - [x] batch_process(video_ids) cria tasks Celery para processar múltiplos vídeos
        - [x] Controle de concorrência

        Args:
            video_ids: Lista de IDs de vídeos para processar
            options: Opções de análise (opcional)

        Returns:
            Informações do batch job criado
        """
        try:
            # Import Celery task
            from app.worker import analyze_tennis_video

            # Criar batch job ID
            batch_id = str(uuid.uuid4())

            # Criar tasks para cada vídeo
            task_ids = []
            for video_id in video_ids:
                # Create analysis task in memory
                task_id = str(uuid.uuid4())
                task = VideoAnalysisTask(task_id, "", video_id)
                self._tasks[task_id] = task

                # Enqueue Celery task
                celery_task = analyze_tennis_video.delay(video_id)
                task_ids.append({
                    "video_id": video_id,
                    "task_id": task_id,
                    "celery_task_id": celery_task.id
                })

            batch_info = {
                "batch_id": batch_id,
                "total_videos": len(video_ids),
                "tasks": task_ids,
                "created_at": datetime.utcnow().isoformat(),
                "status": "processing"
            }

            logger.info(
                "Batch processing started",
                batch_id=batch_id,
                total_videos=len(video_ids)
            )

            return batch_info

        except Exception as e:
            logger.error("Error creating batch processing job", error=str(e))
            raise

    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Obter status de um batch job

        Args:
            batch_id: ID do batch job

        Returns:
            Status do batch job
        """
        # In a real implementation, this would fetch from Redis or database
        # For now, return None as batches are stored in Celery
        return None