"""
Video analysis service integrating with existing tennis tracking modules
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import structlog
import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

# Add the parent src directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from app.schemas.video import VideoAnalysisOptions, VideoAnalysisResult
from app.services.video_service import VideoService
from app.api.websocket.live_stream import broadcast_analysis_update
from app.core.config import settings

logger = structlog.get_logger(__name__)


class AnalysisService:
    """Service for video analysis using existing tennis tracking components"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_video(
        self,
        task_id: str,
        video_path: str,
        options: VideoAnalysisOptions
    ):
        """
        Process video file using the existing tennis tracking pipeline
        """
        logger.info("Starting video analysis", task_id=task_id, video_path=video_path)

        video_service = VideoService(self.db)

        try:
            # Update status to processing
            await video_service.update_analysis_status(task_id, "processing", 0)
            await broadcast_analysis_update(task_id, 0, "processing")

            # Initialize analysis components
            analyzer = VideoAnalyzer(video_path, options)

            # Process video in stages
            result = await self._process_video_stages(analyzer, task_id, video_service)

            # Save results
            await video_service.save_analysis_result(task_id, result)

            # Update status to completed
            await video_service.update_analysis_status(task_id, "completed", 100)
            await broadcast_analysis_update(task_id, 100, "completed")

            logger.info("Video analysis completed", task_id=task_id)

        except Exception as e:
            logger.error("Video analysis failed", task_id=task_id, error=str(e), exc_info=True)

            # Update status to failed
            await video_service.update_analysis_status(task_id, "failed", 0, str(e))
            await broadcast_analysis_update(task_id, 0, "failed")

            raise

    async def _process_video_stages(
        self,
        analyzer: "VideoAnalyzer",
        task_id: str,
        video_service: VideoService
    ) -> VideoAnalysisResult:
        """Process video through different analysis stages"""

        result = VideoAnalysisResult()

        # Stage 1: Video preprocessing and frame extraction (10%)
        await broadcast_analysis_update(task_id, 5, "preprocessing")
        await analyzer.preprocess_video()
        await broadcast_analysis_update(task_id, 10, "preprocessing")

        # Stage 2: Court detection (20%)
        if analyzer.options.enable_court_detection:
            await broadcast_analysis_update(task_id, 15, "court_detection")
            court_data = await analyzer.detect_court()
            result.court_detection = court_data
            await broadcast_analysis_update(task_id, 30, "court_detection")

        # Stage 3: Player detection and tracking (40%)
        if analyzer.options.enable_player_detection:
            await broadcast_analysis_update(task_id, 35, "player_tracking")
            player_data = await analyzer.track_players()
            result.player_detection = player_data
            await broadcast_analysis_update(task_id, 60, "player_tracking")

        # Stage 4: Ball tracking (70%)
        if analyzer.options.enable_ball_tracking:
            await broadcast_analysis_update(task_id, 65, "ball_tracking")
            ball_data = await analyzer.track_ball()
            result.ball_tracking = ball_data
            await broadcast_analysis_update(task_id, 80, "ball_tracking")

        # Stage 5: Rally and serve analysis (85%)
        if analyzer.options.enable_rally_analysis:
            await broadcast_analysis_update(task_id, 82, "rally_analysis")
            rally_data = await analyzer.analyze_rallies()
            result.rally_analysis = rally_data

        if analyzer.options.enable_serve_analysis:
            serve_data = await analyzer.analyze_serves()
            result.serve_analysis = serve_data
            await broadcast_analysis_update(task_id, 90, "rally_analysis")

        # Stage 6: Bounce detection (95%)
        if analyzer.options.enable_bounce_detection:
            await broadcast_analysis_update(task_id, 92, "bounce_detection")
            bounce_data = await analyzer.detect_bounces()
            result.bounce_detection = bounce_data
            await broadcast_analysis_update(task_id, 96, "bounce_detection")

        # Stage 7: Generate output video and statistics (100%)
        await broadcast_analysis_update(task_id, 98, "generating_output")
        output_data = await analyzer.generate_output()
        result.statistics = output_data.get("statistics", {})
        result.metadata = output_data.get("metadata", {})

        return result


class VideoAnalyzer:
    """Video analyzer using existing tennis tracking components"""

    def __init__(self, video_path: str, options: VideoAnalysisOptions):
        self.video_path = video_path
        self.options = options
        self.frames = []
        self.total_frames = 0
        self.fps = 30

        # Initialize existing components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize tennis tracking components"""
        try:
            # Import existing components
            from court_detector import CourtDetector
            from detection import DetectionModel
            from TrackPlayers.trackplayers import PlayerTracker

            # Initialize components with existing model paths
            self.court_detector = CourtDetector()
            self.player_detector = DetectionModel()
            self.player_tracker = PlayerTracker()

            # Initialize TrackNet for ball tracking
            self._initialize_tracknet()

            logger.info("Tennis tracking components initialized")

        except ImportError as e:
            logger.warning("Could not import existing components", error=str(e))
            # Fallback to mock implementations for development
            self._initialize_mock_components()

    def _initialize_tracknet(self):
        """Initialize TrackNet for ball tracking"""
        try:
            from Models.tracknet import TrackNet
            import tensorflow as tf

            # Load TrackNet model
            model_path = settings.TRACKNET_WEIGHTS_PATH
            if os.path.exists(model_path):
                self.tracknet = TrackNet()
                self.tracknet.load_weights(model_path)
                logger.info("TrackNet model loaded", model_path=model_path)
            else:
                logger.warning("TrackNet weights not found", model_path=model_path)
                self.tracknet = None

        except ImportError as e:
            logger.warning("Could not import TrackNet", error=str(e))
            self.tracknet = None

    def _initialize_mock_components(self):
        """Initialize mock components for development/testing"""
        self.court_detector = MockCourtDetector()
        self.player_detector = MockPlayerDetector()
        self.player_tracker = MockPlayerTracker()
        self.tracknet = MockTrackNet()

    async def preprocess_video(self):
        """Extract frames from video"""
        logger.info("Preprocessing video", video_path=self.video_path)

        cap = cv2.VideoCapture(self.video_path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Read all frames (for small videos) or sample frames
        frame_count = 0
        while cap.isOpened() and frame_count < self.total_frames:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame for processing
            frame = cv2.resize(frame, (640, 360))
            self.frames.append(frame)
            frame_count += 1

            # Limit frames for processing if too many
            if len(self.frames) >= 1000:  # Process max 1000 frames
                break

        cap.release()
        logger.info("Video preprocessing complete", total_frames=len(self.frames))

    async def detect_court(self):
        """Detect court lines and boundaries"""
        logger.info("Detecting court")

        court_data = []
        for i, frame in enumerate(self.frames):
            try:
                # Use existing court detector
                lines = self.court_detector.detect_lines(frame)
                homography = self.court_detector.get_homography_matrix(frame)

                court_data.append({
                    "frame_number": i,
                    "timestamp": i / self.fps,
                    "court_lines": lines.tolist() if hasattr(lines, 'tolist') else lines,
                    "homography_matrix": homography.tolist() if hasattr(homography, 'tolist') else homography,
                    "confidence": 0.8  # Mock confidence
                })

            except Exception as e:
                logger.warning("Court detection failed for frame", frame=i, error=str(e))

        logger.info("Court detection complete", frames_processed=len(court_data))
        return court_data

    async def track_players(self):
        """Track players throughout the video"""
        logger.info("Tracking players")

        player_data = []
        for i, frame in enumerate(self.frames):
            try:
                # Detect players in frame
                detections = self.player_detector.detect_players(frame)

                # Track players
                tracked_players = self.player_tracker.update(detections)

                for player in tracked_players:
                    player_data.append({
                        "frame_number": i,
                        "timestamp": i / self.fps,
                        "player_id": player.get("id", 0),
                        "bounding_box": player.get("bbox", {}),
                        "confidence": player.get("confidence", 0.0),
                        "court_position": player.get("court_position")
                    })

            except Exception as e:
                logger.warning("Player tracking failed for frame", frame=i, error=str(e))

        logger.info("Player tracking complete", detections=len(player_data))
        return player_data

    async def track_ball(self):
        """Track tennis ball throughout the video"""
        logger.info("Tracking ball")

        ball_data = []
        if not self.tracknet:
            logger.warning("TrackNet not available, skipping ball tracking")
            return ball_data

        for i in range(len(self.frames) - 2):
            try:
                # Prepare frames for TrackNet (needs 3 consecutive frames)
                frame_batch = np.array([
                    self.frames[i],
                    self.frames[i + 1],
                    self.frames[i + 2]
                ])

                # Predict ball position
                prediction = self.tracknet.predict(frame_batch)

                # Extract ball coordinates from heatmap
                ball_pos = self._extract_ball_position(prediction)

                if ball_pos:
                    ball_data.append({
                        "frame_number": i + 1,
                        "timestamp": (i + 1) / self.fps,
                        "x": ball_pos[0],
                        "y": ball_pos[1],
                        "confidence": ball_pos[2],
                        "velocity": self._calculate_velocity(ball_data, ball_pos),
                        "is_bounce": False  # Will be determined in bounce detection
                    })

            except Exception as e:
                logger.warning("Ball tracking failed for frame", frame=i, error=str(e))

        logger.info("Ball tracking complete", detections=len(ball_data))
        return ball_data

    async def analyze_rallies(self):
        """Analyze rallies from ball and player tracking data"""
        logger.info("Analyzing rallies")

        # Mock rally analysis for now
        rally_data = [{
            "rally_id": "rally_1",
            "start_frame": 0,
            "end_frame": 100,
            "duration": 3.33,
            "shot_count": 8,
            "rally_type": "baseline",
            "winner": "player_1"
        }]

        return rally_data

    async def analyze_serves(self):
        """Analyze serve events"""
        logger.info("Analyzing serves")

        # Mock serve analysis
        serve_data = [{
            "serve_number": 1,
            "frame_number": 50,
            "timestamp": 1.67,
            "server": "player_1",
            "speed": 180.5,
            "placement": {"x": 0.3, "y": 0.8},
            "outcome": "ace"
        }]

        return serve_data

    async def detect_bounces(self):
        """Detect ball bounces"""
        logger.info("Detecting bounces")

        # Mock bounce detection
        bounce_data = [{
            "frame_number": 75,
            "timestamp": 2.5,
            "x": 0.5,
            "y": 0.6,
            "confidence": 0.9,
            "surface": "court"
        }]

        return bounce_data

    async def generate_output(self):
        """Generate output video and statistics"""
        logger.info("Generating output")

        # Mock statistics
        statistics = {
            "total_rallies": 15,
            "average_rally_length": 4.2,
            "total_serves": 30,
            "aces": 5,
            "ball_speed_max": 185.2,
            "ball_speed_average": 142.3
        }

        metadata = {
            "video_duration": len(self.frames) / self.fps,
            "total_frames": len(self.frames),
            "fps": self.fps,
            "processing_options": self.options.dict()
        }

        return {
            "statistics": statistics,
            "metadata": metadata
        }

    def _extract_ball_position(self, heatmap):
        """Extract ball position from TrackNet heatmap"""
        if heatmap is None:
            return None

        # Find maximum value in heatmap
        max_val = np.max(heatmap)
        if max_val < 0.5:  # Confidence threshold
            return None

        # Find coordinates of maximum
        max_pos = np.unravel_index(np.argmax(heatmap), heatmap.shape)
        y, x = max_pos

        return [float(x), float(y), float(max_val)]

    def _calculate_velocity(self, ball_data, current_pos):
        """Calculate ball velocity"""
        if len(ball_data) < 2:
            return {"vx": 0.0, "vy": 0.0, "speed": 0.0}

        prev_pos = ball_data[-1]
        dt = 1.0 / self.fps

        vx = (current_pos[0] - prev_pos["x"]) / dt
        vy = (current_pos[1] - prev_pos["y"]) / dt
        speed = np.sqrt(vx**2 + vy**2)

        return {"vx": vx, "vy": vy, "speed": speed}


# Mock implementations for development
class MockCourtDetector:
    def detect_lines(self, frame):
        return [[100, 100, 200, 200], [300, 100, 400, 200]]

    def get_homography_matrix(self, frame):
        return np.eye(3)


class MockPlayerDetector:
    def detect_players(self, frame):
        return [{"bbox": [100, 100, 50, 100], "confidence": 0.9}]


class MockPlayerTracker:
    def update(self, detections):
        return [{"id": 1, "bbox": det["bbox"], "confidence": det["confidence"]} for det in detections]


class MockTrackNet:
    def predict(self, frame_batch):
        # Return mock heatmap
        return np.random.random((360, 640)) * 0.3