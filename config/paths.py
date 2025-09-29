"""Path configuration for tennis-tracking."""

from pathlib import Path
import os

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Source code directory
SRC_DIR = PROJECT_ROOT / "src"

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
WEIGHTS_DIR = DATA_DIR / "weights"
COURT_CONFIGS_DIR = DATA_DIR / "court_configs"
TRAINING_DATA_DIR = DATA_DIR / "training_data"
SAMPLES_DIR = DATA_DIR / "samples"
INPUT_SAMPLES_DIR = SAMPLES_DIR / "input"
OUTPUT_SAMPLES_DIR = SAMPLES_DIR / "output"

# Configuration directory
CONFIG_DIR = PROJECT_ROOT / "config"

# Tests directory
TESTS_DIR = PROJECT_ROOT / "tests"

# Scripts directory
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Documentation directory
DOCS_DIR = PROJECT_ROOT / "docs"

# Notebooks directory
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Ensure all directories exist
def ensure_directories():
    """Create directories if they don't exist."""
    directories = [
        DATA_DIR,
        WEIGHTS_DIR / "tracknet",
        WEIGHTS_DIR / "yolo",
        WEIGHTS_DIR / "classifiers",
        COURT_CONFIGS_DIR,
        TRAINING_DATA_DIR,
        INPUT_SAMPLES_DIR,
        OUTPUT_SAMPLES_DIR,
        TESTS_DIR / "unit",
        TESTS_DIR / "integration",
        SCRIPTS_DIR,
        DOCS_DIR / "api",
        DOCS_DIR / "guides",
        NOTEBOOKS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Model-specific paths
def get_model_paths():
    """Get paths for all models."""
    return {
        "tracknet": {
            "weights": WEIGHTS_DIR / "tracknet" / "model.1",
            "config": None,
        },
        "yolo": {
            "weights": WEIGHTS_DIR / "yolo" / "yolov3.weights",
            "config": WEIGHTS_DIR / "yolo" / "yolov3.cfg",
        },
        "classifier": {
            "weights": WEIGHTS_DIR / "classifiers" / "clf.pkl",
            "config": None,
        },
    }