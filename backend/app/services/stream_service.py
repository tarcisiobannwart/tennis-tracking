"""
Stream service - manages live camera streams via MediaMTX
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import httpx
from bson import ObjectId

from app.core.config import settings
from app.core.mongodb import get_database, get_collection

logger = logging.getLogger(__name__)


class StreamService:
    """Service for managing live camera streams"""

    def __init__(self):
        self.collection_name = "streams"

    def _get_collection(self):
        return get_collection(self.collection_name)

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
        streams = self._get_collection()
        stream_key = self._generate_stream_key()
        urls = self._build_urls(stream_key)

        stream_doc = {
            "userId": user_id,
            "matchId": match_id,
            "cameraLabel": camera_label,
            "streamKey": stream_key,
            "rtmpUrl": urls["rtmp_url"],
            "hlsUrl": urls["hls_url"],
            "rtspUrl": urls["rtsp_url"],
            "deviceInfo": device_info or {"platform": "unknown"},
            "status": "waiting",
            "isRecording": False,
            "viewerCount": 0,
            "startedAt": None,
            "endedAt": None,
            "createdAt": datetime.utcnow(),
        }

        result = await streams.insert_one(stream_doc)
        stream_doc["_id"] = str(result.inserted_id)

        logger.info(
            "Stream created: %s (key: %s)", stream_doc["_id"], stream_key
        )
        return stream_doc

    async def get_stream(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream by ID"""
        streams = self._get_collection()
        stream = await streams.find_one({"_id": ObjectId(stream_id)})
        if stream:
            stream["_id"] = str(stream["_id"])
        return stream

    async def get_stream_by_key(self, stream_key: str) -> Optional[Dict[str, Any]]:
        """Get stream by stream key"""
        streams = self._get_collection()
        stream = await streams.find_one({"streamKey": stream_key})
        if stream:
            stream["_id"] = str(stream["_id"])
        return stream

    async def list_streams(
        self,
        status: Optional[str] = None,
        match_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List streams with optional filters"""
        streams = self._get_collection()
        query: Dict[str, Any] = {}

        if status:
            query["status"] = status
        if match_id:
            query["matchId"] = match_id
        if user_id:
            query["userId"] = user_id

        cursor = streams.find(query).sort("createdAt", -1)
        result = await cursor.to_list(100)

        for stream in result:
            stream["_id"] = str(stream["_id"])

        return result

    async def update_stream_status(
        self, stream_id: str, status: str
    ) -> Optional[Dict[str, Any]]:
        """Update stream status"""
        streams = self._get_collection()
        update_data: Dict[str, Any] = {"status": status}

        if status == "live":
            update_data["startedAt"] = datetime.utcnow()
        elif status == "ended":
            update_data["endedAt"] = datetime.utcnow()

        result = await streams.find_one_and_update(
            {"_id": ObjectId(stream_id)},
            {"$set": update_data},
            return_document=True,
        )

        if result:
            result["_id"] = str(result["_id"])
            logger.info("Stream %s status updated to %s", stream_id, status)
        return result

    async def end_stream(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """End a stream"""
        return await self.update_stream_status(stream_id, "ended")

    async def set_recording(
        self, stream_id: str, is_recording: bool
    ) -> Optional[Dict[str, Any]]:
        """Toggle recording for a stream"""
        streams = self._get_collection()
        result = await streams.find_one_and_update(
            {"_id": ObjectId(stream_id)},
            {"$set": {"isRecording": is_recording}},
            return_document=True,
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete_stream(self, stream_id: str) -> bool:
        """Delete a stream"""
        streams = self._get_collection()
        result = await streams.delete_one({"_id": ObjectId(stream_id)})
        return result.deleted_count > 0

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


# Global service instance
stream_service = StreamService()
