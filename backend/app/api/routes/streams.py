"""
Streams API routes - Manage live camera streams
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.stream_service import get_stream_service
from app.services.live_processor import live_processor_manager
from app.schemas.stream import (
    StreamCreateRequest,
    StreamUpdateRequest,
    StreamResponse,
    StreamListResponse,
    StreamRecordRequest,
)

router = APIRouter()


def _format_stream_response(stream: dict) -> dict:
    """Format a stream dict to match the response schema"""
    return {
        "id": stream["_id"],
        "match_id": stream.get("matchId"),
        "user_id": stream["userId"],
        "camera_label": stream["cameraLabel"],
        "stream_key": stream["streamKey"],
        "rtmp_url": stream["rtmpUrl"],
        "hls_url": stream["hlsUrl"],
        "status": stream["status"],
        "device_info": stream.get("deviceInfo", {"platform": "unknown"}),
        "started_at": stream.get("startedAt"),
        "ended_at": stream.get("endedAt"),
        "created_at": stream["createdAt"],
        "is_recording": stream.get("isRecording", False),
        "viewer_count": stream.get("viewerCount", 0),
    }


@router.post("", response_model=StreamResponse)
async def create_stream(
    request: StreamCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new stream and get RTMP connection details"""
    service = get_stream_service(db)
    user_id = str(current_user["_id"])
    device_info = request.device_info.dict() if request.device_info else None

    stream = await service.create_stream(
        user_id=user_id,
        match_id=request.match_id,
        camera_label=request.camera_label,
        device_info=device_info,
    )

    return _format_stream_response(stream)


@router.get("", response_model=StreamListResponse)
async def list_streams(
    status: Optional[str] = None,
    match_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List streams with optional filters"""
    service = get_stream_service(db)
    streams = await service.list_streams(
        status=status, match_id=match_id
    )

    active_count = sum(1 for s in streams if s["status"] == "live")

    return {
        "streams": [_format_stream_response(s) for s in streams],
        "total": len(streams),
        "active_count": active_count,
    }


@router.get("/active")
async def get_active_streams(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all currently live streams"""
    service = get_stream_service(db)
    streams = await service.get_active_streams()
    return {
        "streams": [_format_stream_response(s) for s in streams],
        "total": len(streams),
    }


@router.get("/match/{match_id}")
async def get_match_streams(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all streams for a specific match"""
    service = get_stream_service(db)
    streams = await service.get_streams_for_match(match_id)
    active_count = sum(1 for s in streams if s["status"] == "live")

    return {
        "streams": [_format_stream_response(s) for s in streams],
        "total": len(streams),
        "active_count": active_count,
    }


@router.get("/{stream_id}", response_model=StreamResponse)
async def get_stream(
    stream_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get stream details by ID"""
    service = get_stream_service(db)
    stream = await service.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    return _format_stream_response(stream)


@router.patch("/{stream_id}", response_model=StreamResponse)
async def update_stream(
    stream_id: str,
    request: StreamUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update stream settings"""
    service = get_stream_service(db)
    stream = await service.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream["userId"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Apply updates
    if request.is_recording is not None:
        stream = await service.set_recording(stream_id, request.is_recording)

    return _format_stream_response(stream)


@router.delete("/{stream_id}")
async def end_stream(
    stream_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """End and delete a stream"""
    service = get_stream_service(db)
    stream = await service.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream["userId"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")

    # End the stream first, then delete
    if stream["status"] == "live":
        await service.end_stream(stream_id)

    await service.delete_stream(stream_id)
    return {"message": "Stream ended and removed"}


@router.post("/{stream_id}/record")
async def toggle_recording(
    stream_id: str,
    request: StreamRecordRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Start or stop recording for a stream"""
    service = get_stream_service(db)
    stream = await service.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream["userId"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")

    is_recording = request.action == "start"
    updated = await service.set_recording(stream_id, is_recording)

    return {
        "stream_id": stream_id,
        "is_recording": updated.get("isRecording", False) if updated else False,
        "message": f"Recording {'started' if is_recording else 'stopped'}",
    }


@router.post("/{stream_id}/sync")
async def sync_stream_status(
    stream_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Sync stream status with MediaMTX server"""
    service = get_stream_service(db)
    stream = await service.sync_stream_status(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    return _format_stream_response(stream)


@router.post("/{stream_id}/analyze")
async def start_live_analysis(
    stream_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Start CV analysis on a live stream"""
    service = get_stream_service(db)
    stream = await service.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream["status"] != "live":
        raise HTTPException(status_code=400, detail="Stream is not live")

    stream_key = stream["streamKey"]
    if live_processor_manager.is_processing(stream_key):
        raise HTTPException(status_code=409, detail="Already processing this stream")

    await live_processor_manager.start_processing(
        stream_key=stream_key,
        match_id=stream.get("matchId"),
    )

    return {
        "stream_id": stream_id,
        "message": "Live analysis started",
        "processing": True,
    }


@router.delete("/{stream_id}/analyze")
async def stop_live_analysis(
    stream_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Stop CV analysis on a live stream"""
    service = get_stream_service(db)
    stream = await service.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    stopped = await live_processor_manager.stop_processing(stream["streamKey"])

    return {
        "stream_id": stream_id,
        "message": "Live analysis stopped" if stopped else "No active analysis found",
        "processing": False,
    }


@router.get("/processing/active")
async def get_active_processors(
    current_user=Depends(get_current_user),
):
    """Get list of streams currently being processed by CV"""
    active = live_processor_manager.get_active_processors()
    return {"active_processors": active, "count": len(active)}
