# Tennis Tracking - Architecture Overview

## System Architecture

The tennis tracking system is organized into modular components that work together to process tennis videos and extract meaningful information about ball movement, player positions, and court detection.

## Core Components

### 1. Detection Module (`src/detection/`)

#### Ball Detection (`src/detection/ball/`)
- **TrackNet**: Deep learning model for ball position detection
- Generates heatmaps indicating ball position probability
- Processes 3 consecutive frames for movement context

#### Court Detection (`src/detection/court/`)
- **Court Detector**: Identifies court lines and boundaries
- **Court Reference**: Geometric reference for court transformations
- Uses Hough transform and perspective transformation

#### Player Detection (`src/detection/players/`)
- **Player Detector**: Identifies and localizes players
- Uses Faster R-CNN ResNet50 for person detection
- Filters spectators based on court proximity

### 2. Tracking Module (`src/tracking/`)

#### SORT Tracking (`src/tracking/sort/`)
- Multiple object tracking algorithm
- Kalman filter-based prediction
- Data association for consistent IDs

#### Player Tracker
- Specialized tracking for tennis players
- Maintains player identities across frames

### 3. Analysis Module (`src/analysis/`)
- Bounce prediction using machine learning
- Game statistics computation
- Minimap generation for court overview

### 4. Core Module (`src/core/`)
- Main processing pipeline
- Video I/O handling
- Visualization and rendering

### 5. Utilities (`src/utils/`)
- Device detection (GPU/CPU)
- File handling utilities
- Geometric calculations

## Data Flow

1. **Video Input** → Frame extraction
2. **Ball Detection** → TrackNet heatmap generation
3. **Court Detection** → Line identification and perspective correction
4. **Player Detection** → Person bounding boxes with filtering
5. **Tracking** → Consistent ID assignment across frames
6. **Analysis** → Bounce prediction and statistics
7. **Visualization** → Overlay tracking data on frames
8. **Video Output** → Reconstructed video with annotations

## Configuration

All system configuration is centralized in the `config/` directory:
- `settings.py`: General system settings
- `paths.py`: File and directory paths
- Model-specific configurations

## Data Management

The `data/` directory contains:
- **weights/**: Pre-trained model weights
- **court_configs/**: Court reference images
- **training_data/**: Training datasets
- **samples/**: Input/output video samples