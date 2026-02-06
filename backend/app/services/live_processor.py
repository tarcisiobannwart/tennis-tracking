"""
Live stream processor - consumes RTSP streams from MediaMTX
and runs CV analysis in real-time, broadcasting results via WebSocket.
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any

import cv2
import numpy as np

from app.core.config import settings
from app.api.websocket.live_stream import manager

logger = logging.getLogger(__name__)


class LiveStreamProcessor:
    """Processes a live RTSP stream from MediaMTX with CV models"""

    def __init__(self, stream_key: str, match_id: Optional[str] = None):
        self.stream_key = stream_key
        self.match_id = match_id
        self.rtsp_url = f"{settings.MEDIAMTX_RTSP_URL}/court/{stream_key}"
        self._running = False
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame_count = 0
        self._fps = 0.0
        self._last_fps_time = 0.0
        self._fps_frame_count = 0

        # CV components (lazy-loaded)
        self._court_detector = None
        self._player_detector = None
        self._tracknet = None
        self._frame_buffer: list = []

    def _init_cv_components(self):
        """Initialize CV components (lazy loading to avoid import overhead)"""
        try:
            from court_detector import CourtDetector
            self._court_detector = CourtDetector()
            logger.info("Court detector initialized")
        except ImportError:
            logger.warning("Court detector not available")

        try:
            from detection import DetectionModel
            self._player_detector = DetectionModel()
            logger.info("Player detector initialized")
        except ImportError:
            logger.warning("Player detector not available")

        try:
            from Models.tracknet import TrackNet
            import os
            model_path = settings.TRACKNET_WEIGHTS_PATH
            if os.path.exists(model_path):
                self._tracknet = TrackNet()
                self._tracknet.load_weights(model_path)
                logger.info("TrackNet loaded")
            else:
                logger.warning("TrackNet weights not found: %s", model_path)
        except ImportError:
            logger.warning("TrackNet not available")

    async def start(self):
        """Start processing the live stream"""
        if self._running:
            logger.warning("Processor already running for %s", self.stream_key)
            return

        logger.info("Starting live processor for stream: %s", self.stream_key)
        self._running = True
        self._init_cv_components()

        # Run the capture loop in a thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._connect_to_stream)

        if self._cap is None or not self._cap.isOpened():
            logger.error("Failed to connect to RTSP stream: %s", self.rtsp_url)
            self._running = False
            return

        # Start the processing loop
        asyncio.create_task(self._process_loop())
        logger.info("Live processor started for %s", self.stream_key)

    def _connect_to_stream(self):
        """Connect to the RTSP stream (runs in thread)"""
        try:
            self._cap = cv2.VideoCapture(self.rtsp_url)
            # Set buffer size to reduce latency
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception as e:
            logger.error("Error connecting to stream: %s", e)
            self._cap = None

    async def stop(self):
        """Stop processing"""
        self._running = False
        if self._cap:
            self._cap.release()
            self._cap = None
        logger.info("Live processor stopped for %s", self.stream_key)

    async def _process_loop(self):
        """Main processing loop - reads frames and runs CV analysis"""
        loop = asyncio.get_event_loop()
        self._last_fps_time = time.time()

        while self._running:
            try:
                # Read frame in thread to avoid blocking
                ret, frame = await loop.run_in_executor(
                    None, self._read_frame
                )

                if not ret or frame is None:
                    # Stream might have ended or connection lost
                    await asyncio.sleep(0.5)
                    # Try to reconnect
                    await loop.run_in_executor(None, self._reconnect)
                    continue

                self._frame_count += 1
                self._fps_frame_count += 1

                # Calculate FPS every second
                now = time.time()
                if now - self._last_fps_time >= 1.0:
                    self._fps = self._fps_frame_count / (now - self._last_fps_time)
                    self._fps_frame_count = 0
                    self._last_fps_time = now

                # Process every N frames to manage load (e.g., every 3rd frame)
                if self._frame_count % 3 != 0:
                    continue

                # Resize for processing
                frame_resized = cv2.resize(frame, (640, 360))

                # Run CV analysis
                analysis_result = await loop.run_in_executor(
                    None, self._analyze_frame, frame_resized
                )

                # Broadcast result via WebSocket
                await self._broadcast_frame_update(analysis_result)

                # Small sleep to prevent CPU saturation
                await asyncio.sleep(0.01)

            except Exception as e:
                logger.error("Error in processing loop: %s", e)
                await asyncio.sleep(1.0)

    def _read_frame(self):
        """Read a single frame from the video capture (runs in thread)"""
        if self._cap and self._cap.isOpened():
            return self._cap.read()
        return False, None

    def _reconnect(self):
        """Try to reconnect to the stream"""
        if self._cap:
            self._cap.release()
        try:
            self._cap = cv2.VideoCapture(self.rtsp_url)
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception as e:
            logger.error("Reconnect failed: %s", e)

    def _analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Run CV analysis on a single frame (runs in thread)"""
        result: Dict[str, Any] = {
            "frame_number": self._frame_count,
            "timestamp": time.time(),
            "fps": round(self._fps, 1),
        }

        # Court detection
        if self._court_detector:
            try:
                lines = self._court_detector.detect_lines(frame)
                result["court_detection"] = {
                    "lines": lines.tolist() if hasattr(lines, "tolist") else lines,
                    "confidence": 0.8,
                }
            except Exception:
                pass

        # Player detection
        if self._player_detector:
            try:
                detections = self._player_detector.detect_players(frame)
                players = []
                for det in detections if detections else []:
                    players.append({
                        "bbox": det.get("bbox", []),
                        "confidence": det.get("confidence", 0),
                    })
                result["player_detection"] = players

                # Map to player positions
                if len(players) >= 1:
                    bbox = players[0].get("bbox", [0, 0, 0, 0])
                    result["player1_position"] = {
                        "x": bbox[0] + bbox[2] / 2 if len(bbox) >= 4 else 0,
                        "y": bbox[1] + bbox[3] if len(bbox) >= 4 else 0,
                    }
                if len(players) >= 2:
                    bbox = players[1].get("bbox", [0, 0, 0, 0])
                    result["player2_position"] = {
                        "x": bbox[0] + bbox[2] / 2 if len(bbox) >= 4 else 0,
                        "y": bbox[1] + bbox[3] if len(bbox) >= 4 else 0,
                    }
            except Exception:
                pass

        # Ball tracking (needs 3 consecutive frames)
        self._frame_buffer.append(frame)
        if len(self._frame_buffer) > 3:
            self._frame_buffer.pop(0)

        if self._tracknet and len(self._frame_buffer) == 3:
            try:
                batch = np.array(self._frame_buffer)
                prediction = self._tracknet.predict(batch)
                ball_pos = self._extract_ball_position(prediction)
                if ball_pos:
                    result["ball_position"] = {
                        "x": ball_pos[0],
                        "y": ball_pos[1],
                        "confidence": ball_pos[2],
                    }
            except Exception:
                pass

        return result

    def _extract_ball_position(self, heatmap) -> Optional[list]:
        """Extract ball position from TrackNet heatmap"""
        if heatmap is None:
            return None
        max_val = np.max(heatmap)
        if max_val < 0.5:
            return None
        max_pos = np.unravel_index(np.argmax(heatmap), heatmap.shape)
        y, x = max_pos
        return [float(x), float(y), float(max_val)]

    async def _broadcast_frame_update(self, analysis_result: Dict[str, Any]):
        """Send frame analysis to connected WebSocket clients"""
        message = {
            "type": "frame_update",
            "stream_key": self.stream_key,
            "data": analysis_result,
        }

        if self.match_id:
            await manager.send_to_match(self.match_id, message)
        else:
            await manager.send_global(message)


class LiveProcessorManager:
    """Manages multiple live stream processors"""

    def __init__(self):
        self._processors: Dict[str, LiveStreamProcessor] = {}

    async def start_processing(
        self, stream_key: str, match_id: Optional[str] = None
    ) -> bool:
        """Start processing a stream"""
        if stream_key in self._processors:
            logger.warning("Processor already exists for %s", stream_key)
            return False

        processor = LiveStreamProcessor(stream_key, match_id)
        self._processors[stream_key] = processor
        await processor.start()
        return True

    async def stop_processing(self, stream_key: str) -> bool:
        """Stop processing a stream"""
        processor = self._processors.pop(stream_key, None)
        if processor:
            await processor.stop()
            return True
        return False

    async def stop_all(self):
        """Stop all active processors"""
        for key in list(self._processors.keys()):
            await self.stop_processing(key)

    def get_active_processors(self) -> list:
        """Get list of actively processed stream keys"""
        return list(self._processors.keys())

    def is_processing(self, stream_key: str) -> bool:
        """Check if a stream is being processed"""
        return stream_key in self._processors


# Global manager instance
live_processor_manager = LiveProcessorManager()
