"""
WebSocket endpoints for live match streaming and real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Set
import json
import asyncio
import structlog

from app.core.database import get_db
from app.services.websocket_service import WebSocketService
from app.services.match_service import MatchService

router = APIRouter()
logger = structlog.get_logger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""

    def __init__(self):
        # Active connections by match_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Global connections (for system-wide events)
        self.global_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, match_id: str = None):
        """Accept WebSocket connection"""
        await websocket.accept()

        if match_id:
            if match_id not in self.active_connections:
                self.active_connections[match_id] = set()
            self.active_connections[match_id].add(websocket)
            logger.info("WebSocket connected to match", match_id=match_id)
        else:
            self.global_connections.add(websocket)
            logger.info("Global WebSocket connected")

    def disconnect(self, websocket: WebSocket, match_id: str = None):
        """Remove WebSocket connection"""
        if match_id and match_id in self.active_connections:
            self.active_connections[match_id].discard(websocket)
            if not self.active_connections[match_id]:
                del self.active_connections[match_id]
            logger.info("WebSocket disconnected from match", match_id=match_id)
        else:
            self.global_connections.discard(websocket)
            logger.info("Global WebSocket disconnected")

    async def send_to_match(self, match_id: str, data: dict):
        """Send data to all connections for a specific match"""
        if match_id in self.active_connections:
            message = json.dumps(data)
            disconnected = set()

            for websocket in self.active_connections[match_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error("Failed to send message", error=str(e))
                    disconnected.add(websocket)

            # Remove disconnected websockets
            for websocket in disconnected:
                self.active_connections[match_id].discard(websocket)

    async def send_global(self, data: dict):
        """Send data to all global connections"""
        message = json.dumps(data)
        disconnected = set()

        for websocket in self.global_connections:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error("Failed to send global message", error=str(e))
                disconnected.add(websocket)

        # Remove disconnected websockets
        for websocket in disconnected:
            self.global_connections.discard(websocket)

    async def broadcast_to_all(self, data: dict):
        """Broadcast data to all active connections"""
        await self.send_global(data)
        for match_id in self.active_connections:
            await self.send_to_match(match_id, data)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/live/{match_id}")
async def websocket_match_endpoint(
    websocket: WebSocket,
    match_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for live match updates
    """
    await manager.connect(websocket, match_id)

    try:
        # Verify match exists
        match_service = MatchService(db)
        match = await match_service.get_match(match_id)

        if not match:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Match {match_id} not found"
            }))
            await websocket.close()
            return

        # Send initial match state
        await websocket.send_text(json.dumps({
            "type": "match_state",
            "match_id": match_id,
            "data": {
                "status": match.status,
                "player1_sets": match.player1_sets,
                "player2_sets": match.player2_sets,
                "current_set": match.current_set
            }
        }))

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0  # 30 second timeout
                )

                # Parse incoming message
                try:
                    data = json.loads(message)
                    await handle_client_message(websocket, match_id, data, db)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))

            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text(json.dumps({
                    "type": "ping",
                    "timestamp": asyncio.get_event_loop().time()
                }))

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", match_id=match_id)
    except Exception as e:
        logger.error("WebSocket error", match_id=match_id, error=str(e))
    finally:
        manager.disconnect(websocket, match_id)


@router.websocket("/ws/global")
async def websocket_global_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for global system updates
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "message": "Connected to Tennis Tracking global updates"
        }))

        # Keep connection alive
        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # 60 second timeout for global connections
                )

                # Handle global messages (admin commands, etc.)
                try:
                    data = json.loads(message)
                    await handle_global_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))

            except asyncio.TimeoutError:
                # Send ping
                await websocket.send_text(json.dumps({
                    "type": "ping",
                    "timestamp": asyncio.get_event_loop().time()
                }))

    except WebSocketDisconnect:
        logger.info("Global WebSocket disconnected")
    except Exception as e:
        logger.error("Global WebSocket error", error=str(e))
    finally:
        manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, match_id: str, data: dict, db: AsyncSession):
    """Handle incoming client messages"""
    message_type = data.get("type")

    if message_type == "pong":
        # Client responded to ping
        pass

    elif message_type == "subscribe_events":
        # Client wants to subscribe to specific event types
        event_types = data.get("event_types", [])
        await websocket.send_text(json.dumps({
            "type": "subscription_confirmed",
            "event_types": event_types
        }))

    elif message_type == "request_current_state":
        # Client requests current match state
        match_service = MatchService(db)
        match = await match_service.get_match(match_id)

        if match:
            await websocket.send_text(json.dumps({
                "type": "current_state",
                "data": {
                    "match_id": match_id,
                    "status": match.status,
                    "score": {
                        "player1_sets": match.player1_sets,
                        "player2_sets": match.player2_sets,
                        "current_set": match.current_set
                    }
                }
            }))

    else:
        logger.warning("Unknown message type", type=message_type, match_id=match_id)


async def handle_global_message(websocket: WebSocket, data: dict):
    """Handle incoming global messages"""
    message_type = data.get("type")

    if message_type == "pong":
        # Client responded to ping
        pass

    elif message_type == "admin_command":
        # Handle admin commands (if authorized)
        command = data.get("command")
        logger.info("Admin command received", command=command)

        # Add admin authentication and command handling here
        await websocket.send_text(json.dumps({
            "type": "admin_response",
            "message": f"Command '{command}' received (not implemented)"
        }))

    else:
        logger.warning("Unknown global message type", type=message_type)


# Helper functions for external services to broadcast events
async def broadcast_match_event(match_id: str, event_type: str, event_data: dict):
    """Broadcast match event to all connected clients for that match"""
    await manager.send_to_match(match_id, {
        "type": "match_event",
        "event_type": event_type,
        "match_id": match_id,
        "data": event_data,
        "timestamp": asyncio.get_event_loop().time()
    })


async def broadcast_global_event(event_type: str, event_data: dict):
    """Broadcast global event to all connected clients"""
    await manager.send_global({
        "type": "global_event",
        "event_type": event_type,
        "data": event_data,
        "timestamp": asyncio.get_event_loop().time()
    })


async def broadcast_analysis_update(task_id: str, progress: int, status: str, match_id: str = None):
    """Broadcast video analysis progress update"""
    update_data = {
        "type": "analysis_update",
        "task_id": task_id,
        "progress": progress,
        "status": status,
        "timestamp": asyncio.get_event_loop().time()
    }

    if match_id:
        await manager.send_to_match(match_id, update_data)
    else:
        await manager.send_global(update_data)