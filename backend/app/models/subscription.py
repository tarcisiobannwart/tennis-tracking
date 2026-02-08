"""
Subscription Pydantic models
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SubscriptionEvent(BaseModel):
    """Stripe webhook event log"""
    userId: str
    stripeEventId: str
    eventType: str
    data: dict = Field(default_factory=dict)
    processed: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class PlanInfo(BaseModel):
    """Plan info for API responses"""
    id: str
    name: str
    price: int  # centavos
    currency: str = "brl"
    interval: str = "month"
    features: dict = Field(default_factory=dict)


PLAN_LIMITS = {
    "rally": {
        "name": "Rally",
        "price": 0,
        "videos_per_month": 3,
        "max_video_duration": 300,  # 5 min em segundos
        "models": ["basic"],
        "history_days": 7,
        "max_team_members": 1,
        "api_access": False,
    },
    "match_point": {
        "name": "Match Point",
        "price": 9700,  # R$97 em centavos
        "videos_per_month": -1,  # ilimitado
        "max_video_duration": 3600,  # 60 min
        "models": ["basic", "tracknet", "yolo", "faster_rcnn"],
        "history_days": 90,
        "max_team_members": 1,
        "api_access": False,
        "trial_days": 14,
    },
    "grand_slam": {
        "name": "Grand Slam",
        "price": 29700,  # R$297 em centavos
        "videos_per_month": -1,  # ilimitado
        "max_video_duration": 10800,  # 3h
        "models": ["basic", "tracknet", "yolo", "faster_rcnn"],
        "history_days": -1,  # ilimitado
        "max_team_members": 10,
        "api_access": True,
    },
}
