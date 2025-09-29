"""General configuration settings for tennis-tracking."""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
WEIGHTS_DIR = DATA_DIR / "weights"
COURT_CONFIGS_DIR = DATA_DIR / "court_configs"
TRAINING_DATA_DIR = DATA_DIR / "training_data"
SAMPLES_DIR = DATA_DIR / "samples"

# Model weights paths
TRACKNET_WEIGHTS = WEIGHTS_DIR / "tracknet" / "model.1"
YOLO_WEIGHTS = WEIGHTS_DIR / "yolo" / "yolov3.weights"
YOLO_CONFIG = WEIGHTS_DIR / "yolo" / "yolov3.cfg"
CLASSIFIER_WEIGHTS = WEIGHTS_DIR / "classifiers" / "clf.pkl"

# Default video processing settings
DEFAULT_VIDEO_SETTINGS = {
    "minimap": False,
    "bounce": False,
    "fps": 30,
    "output_format": "mp4",
}

# Court detection settings
COURT_DETECTION_SETTINGS = {
    "court_reference": COURT_CONFIGS_DIR / "court_reference.png",
    "line_threshold": 100,
    "min_line_length": 50,
    "max_line_gap": 20,
}

# Ball tracking settings
BALL_TRACKING_SETTINGS = {
    "heatmap_threshold": 0.5,
    "smoothing_window": 3,
    "max_missing_frames": 10,
}

# Player tracking settings
PLAYER_TRACKING_SETTINGS = {
    "confidence_threshold": 0.7,
    "max_disappeared": 50,
    "max_distance": 100,
}

# Device settings
DEVICE_SETTINGS = {
    "prefer_gpu": True,
    "gpu_memory_fraction": 0.8,
}