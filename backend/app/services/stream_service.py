"""
Stream service - manages live camera streams via MediaMTX
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import httpx
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.sql.stream import Stream, StreamStatusEnum

logger = logging.getLogger(__name__)


class StreamService:
    """Service for managing live camera streams"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_stream_key(self) -> str:
        """Generate a unique stream key for RTMP authentication"""
        return uuid.uuid4().hex[:16]

    def _build_stream_path(self, stream_key: str) -> str:
        """Build the MediaMTX path for a stream"""
        return f"court/{stream_key}"

    def _build_urls(self, stream_key: str) -> Dict[str, str]:
        """Build RTMP, HLS and RTSP URLs for a stream"""
        path = self._build_stream_path(stream_key)
        return {
            "rtmp_url": f"{settings.MEDIAMTX_RTMP_URL}/{path}",
            "hls_url": f"{settings.MEDIAMTX_HLS_URL}/{path}",
            "rtsp_url": f"{settings.MEDIAMTX_RTSP_URL}/{path}",
        }

    async def create_stream(
        self,
        user_id: str,
        match_id: Optional[str] = None,
        camera_label: str = "Camera 1",
        device_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new stream and return connection details"""
        stream_key = self._generate_stream_key()
        urls = self._build_urls(stream_key)

        stream = Stream(
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            match_id=match_id,
            camera_label=camera_label,
            stream_key=stream_key,
            rtmp_url=urls["rtmp_url"],
            hls_url=urls["hls_url"],
            rtsp_url=urls["rtsp_url"],
            device_info=device_info or {"platform": "unknown"},
            status=StreamStatusEnum.WAITING.value,
            is_recording=False,
            viewer_count=0,
        )

        self.db.add(stream)
        await self.db.flush()
        await self.db.refresh(stream)

        logger.info(
            "Stream created: %s (key: %s)", str(stream.id), stream_key
        )

        return {
            "_id": str(stream.id),
            "userId": str(stream.user_id),
            "matchId": stream.match_id,
            "cameraLabel": stream.camera_label,
            "streamKey": stream.stream_key,
            "rtmpUrl": stream.rtmp_url,
            "hlsUrl": stream.hls_url,
            "rtspUrl": stream.rtsp_url,
            "deviceInfo": stream.device_info,
            "status": stream.status,
            "isRecording": stream.is_recording,
            "viewerCount": stream.viewer_count,
            "startedAt": stream.started_at,
            "endedAt": stream.ended_at,
            "createdAt": stream.created_at,
        }

    async def get_stream(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream by ID"""
        stmt = select(Stream).where(Stream.id == uuid.UUID(stream_id))
        result = await self.db.execute(stmt)
        stream = result.scalar_one_or_none()

        if not stream:
            return None

        return {
            "_id": str(stream.id),
            "userId": str(stream.user_id),
            "matchId": stream.match_id,
            "cameraLabel": stream.camera_label,
            "streamKey": stream.stream_key,
            "rtmpUrl": stream.rtmp_url,
            "hlsUrl": stream.hls_url,
            "rtspUrl": stream.rtsp_url,
            "deviceInfo": stream.device_info,
            "status": stream.status,
            "isRecording": stream.is_recording,
            "viewerCount": stream.viewer_count,
            "startedAt": stream.started_at,
            "endedAt": stream.ended_at,
            "createdAt": stream.created_at,
        }

    async def get_stream_by_key(self, stream_key: str) -> Optional[Dict[str, Any]]:
        """Get stream by stream key"""
        stmt = select(Stream).where(Stream.stream_key == stream_key)
        result = await self.db.execute(stmt)
        stream = result.scalar_one_or_none()

        if not stream:
            return None

        return {
            "_id": str(stream.id),
            "userId": str(stream.user_id),
            "matchId": stream.match_id,
            "cameraLabel": stream.camera_label,
            "streamKey": stream.stream_key,
            "rtmpUrl": stream.rtmp_url,
            "hlsUrl": stream.hls_url,
            "rtspUrl": stream.rtsp_url,
            "deviceInfo": stream.device_info,
            "status": stream.status,
            "isRecording": stream.is_recording,
            "viewerCount": stream.viewer_count,
            "startedAt": stream.started_at,
            "endedAt": stream.ended_at,
            "createdAt": stream.created_at,
        }

    async def list_streams(
        self,
        status: Optional[str] = None,
        match_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List streams with optional filters"""
        stmt = select(Stream)

        conditions = []
        if status:
            conditions.append(Stream.status == status)
        if match_id:
            conditions.append(Stream.match_id == match_id)
        if user_id:
            conditions.append(Stream.user_id == uuid.UUID(user_id))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(Stream.created_at.desc()).limit(100)

        result = await self.db.execute(stmt)
        streams = result.scalars().all()

        return [
            {
                "_id": str(stream.id),
                "userId": str(stream.user_id),
                "matchId": stream.match_id,
                "cameraLabel": stream.camera_label,
                "streamKey": stream.stream_key,
                "rtmpUrl": stream.rtmp_url,
                "hlsUrl": stream.hls_url,
                "rtspUrl": stream.rtsp_url,
                "deviceInfo": stream.device_info,
                "status": stream.status,
                "isRecording": stream.is_recording,
                "viewerCount": stream.viewer_count,
                "startedAt": stream.started_at,
                "endedAt": stream.ended_at,
                "createdAt": stream.created_at,
            }
            for stream in streams
        ]

    async def update_stream_status(
        self, stream_id: str, status: str
    ) -> Optional[Dict[str, Any]]:
        """Update stream status"""
        stmt = select(Stream).where(Stream.id == uuid.UUID(stream_id))
        result = await self.db.execute(stmt)
        stream = result.scalar_one_or_none()

        if not stream:
            return None

        stream.status = status

        if status == "live":
            stream.started_at = datetime.utcnow()
        elif status == "ended":
            stream.ended_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(stream)

        logger.info("Stream %s status updated to %s", stream_id, status)

        return {
            "_id": str(stream.id),
            "userId": str(stream.user_id),
            "matchId": stream.match_id,
            "cameraLabel": stream.camera_label,
            "streamKey": stream.stream_key,
            "rtmpUrl": stream.rtmp_url,
            "hlsUrl": stream.hls_url,
            "rtspUrl": stream.rtsp_url,
            "deviceInfo": stream.device_info,
            "status": stream.status,
            "isRecording": stream.is_recording,
            "viewerCount": stream.viewer_count,
            "startedAt": stream.started_at,
            "endedAt": stream.ended_at,
            "createdAt": stream.created_at,
        }

    async def end_stream(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """End a stream"""
        return await self.update_stream_status(stream_id, "ended")

    async def set_recording(
        self, stream_id: str, is_recording: bool
    ) -> Optional[Dict[str, Any]]:
        """Toggle recording for a stream"""
        stmt = select(Stream).where(Stream.id == uuid.UUID(stream_id))
        result = await self.db.execute(stmt)
        stream = result.scalar_one_or_none()

        if not stream:
            return None

        stream.is_recording = is_recording
        await self.db.flush()
        await self.db.refresh(stream)

        return {
            "_id": str(stream.id),
            "userId": str(stream.user_id),
            "matchId": stream.match_id,
            "cameraLabel": stream.camera_label,
            "streamKey": stream.stream_key,
            "rtmpUrl": stream.rtmp_url,
            "hlsUrl": stream.hls_url,
            "rtspUrl": stream.rtsp_url,
            "deviceInfo": stream.device_info,
            "status": stream.status,
            "isRecording": stream.is_recording,
            "viewerCount": stream.viewer_count,
            "startedAt": stream.started_at,
            "endedAt": stream.ended_at,
            "createdAt": stream.created_at,
        }

    async def delete_stream(self, stream_id: str) -> bool:
        """Delete a stream"""
        stmt = delete(Stream).where(Stream.id == uuid.UUID(stream_id))
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def get_streams_for_match(
        self, match_id: str
    ) -> List[Dict[str, Any]]:
        """Get all streams associated with a match"""
        return await self.list_streams(match_id=match_id)

    async def get_active_streams(self) -> List[Dict[str, Any]]:
        """Get all currently live streams"""
        return await self.list_streams(status="live")

    async def check_mediamtx_stream_status(self, stream_key: str) -> Optional[Dict[str, Any]]:
        """Check if a stream is active on MediaMTX via its API"""
        path = self._build_stream_path(stream_key)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.MEDIAMTX_API_URL}/v3/paths/get/{path}"
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.warning("Failed to check MediaMTX status: %s", e)
        return None

    async def sync_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Sync stream status with MediaMTX"""
        stream = await self.get_stream(stream_id)
        if not stream:
            return None

        mtx_status = await self.check_mediamtx_stream_status(stream["streamKey"])

        if mtx_status and stream["status"] != "live":
            return await self.update_stream_status(stream_id, "live")
        elif not mtx_status and stream["status"] == "live":
            return await self.update_stream_status(stream_id, "ended")

        return stream


# Global service instance factory
def get_stream_service(db: AsyncSession) -> StreamService:
    """Factory function for stream service"""
    return StreamService(db)
