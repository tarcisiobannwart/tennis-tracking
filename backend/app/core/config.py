"""
Application configuration settings
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Tennis Tracking API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database - MongoDB
    MONGODB_URL: str = "mongodb://admin:tennis_admin_2024@localhost:27017/tennis_tracking?authSource=admin"
    DATABASE_NAME: str = "tennis_tracking"

    # Legacy SQLite (for migration)
    DATABASE_URL: str = "sqlite+aiosqlite:///./tennis_tracking.db"

    # Redis (for caching and Celery)
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev
        "http://localhost:5173",  # Vite dev
        "http://localhost:8080",  # Vue dev
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv"]

    # Video processing
    TEMP_DIR: str = "./temp"
    OUTPUT_DIR: str = "./output"

    # Computer Vision Models
    TRACKNET_WEIGHTS_PATH: str = "../WeightsTracknet/model.1"
    YOLO_WEIGHTS_PATH: str = "../Yolov3/yolov3.weights"
    YOLO_CONFIG_PATH: str = "../Yolov3/yolov3.cfg"
    YOLO_CLASSES_PATH: str = "../Yolov3/coco.names"

    # Analysis settings
    VIDEO_PROCESSING_TIMEOUT: int = 3600  # 1 hour
    FRAME_RATE: int = 30
    COURT_DETECTION_CONFIDENCE: float = 0.5
    PLAYER_DETECTION_CONFIDENCE: float = 0.6

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()