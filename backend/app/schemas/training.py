"""
Training Pydantic schemas (re-exports from models for backwards compatibility)
"""

from app.models.training import (
    DrillTypeCreate,
    DrillTypeResponse,
    TrainingDrillCreate,
    TrainingDrillResponse,
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingSessionResponse,
)

__all__ = [
    "DrillTypeCreate",
    "DrillTypeResponse",
    "TrainingDrillCreate",
    "TrainingDrillResponse",
    "TrainingSessionCreate",
    "TrainingSessionUpdate",
    "TrainingSessionResponse",
]
