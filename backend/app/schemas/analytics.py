"""
Analytics Pydantic schemas
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class PerformanceMetrics(BaseModel):
    """Schema for performance metrics"""
    serve_percentage: float
    ace_percentage: float
    double_fault_percentage: float
    first_serve_points_won: float
    second_serve_points_won: float
    break_points_saved: float
    break_points_converted: float
    winners: int
    unforced_errors: int
    forced_errors: int
    net_points_won: float
    baseline_points_won: float
    average_rally_length: float
    distance_covered: Optional[float] = None
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None


class PerformanceAnalytics(BaseModel):
    """Schema for performance analytics"""
    match_id: str
    player_id: str
    metrics: PerformanceMetrics
    shot_analysis: Dict[str, Any] = {}
    movement_analysis: Dict[str, Any] = {}
    tactical_analysis: Dict[str, Any] = {}
    comparison_to_average: Dict[str, float] = {}
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []

    class Config:
        from_attributes = True


class HeatmapPoint(BaseModel):
    """Schema for heatmap data point"""
    x: float
    y: float
    intensity: float
    count: int


class HeatmapData(BaseModel):
    """Schema for court heatmap data"""
    match_id: str
    player_id: str
    data_type: str  # "position", "shots", "serves", "returns"
    points: List[HeatmapPoint]
    court_dimensions: Dict[str, float]
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class PlayerComparison(BaseModel):
    """Schema for player comparison analytics"""
    player1_id: str
    player2_id: str
    comparison_period: str  # "match", "season", "career"
    metrics_comparison: Dict[str, Dict[str, float]]
    head_to_head: Dict[str, Any]
    surface_performance: Dict[str, Dict[str, float]]
    recent_form: Dict[str, List[str]]
    statistical_insights: List[str] = []

    class Config:
        from_attributes = True


class TrendDataPoint(BaseModel):
    """Schema for trend data point"""
    date: datetime
    value: float
    match_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class TrendAnalysis(BaseModel):
    """Schema for trend analysis"""
    player_id: str
    metric: str
    period: str  # "week", "month", "quarter", "year"
    data_points: List[TrendDataPoint]
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0-1
    statistical_significance: bool
    insights: List[str] = []
    predictions: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class MatchInsights(BaseModel):
    """Schema for match insights"""
    match_id: str
    key_moments: List[Dict[str, Any]]
    turning_points: List[Dict[str, Any]]
    momentum_shifts: List[Dict[str, Any]]
    tactical_patterns: List[Dict[str, Any]]
    performance_highlights: List[Dict[str, Any]]
    areas_for_improvement: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class ShotAnalysis(BaseModel):
    """Schema for shot analysis"""
    shot_type: str
    court_position: Dict[str, float]
    target_position: Dict[str, float]
    speed: Optional[float] = None
    spin: Optional[Dict[str, float]] = None
    accuracy: float
    outcome: str
    effectiveness_score: float

    class Config:
        from_attributes = True


class RallyAnalysis(BaseModel):
    """Schema for rally analysis"""
    rally_id: str
    match_id: str
    point_id: str
    duration: float
    shot_count: int
    shots: List[ShotAnalysis]
    rally_type: str  # "baseline", "net", "mixed"
    intensity: float
    complexity: float
    outcome: str
    winner_player_id: str

    class Config:
        from_attributes = True