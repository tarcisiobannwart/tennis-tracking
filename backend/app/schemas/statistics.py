"""
Statistics Pydantic schemas - TT-133
Schemas para dashboard de estatisticas avancadas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class OverallStats(BaseModel):
    """Resumo geral de vitorias e derrotas"""
    total_matches: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0


class BreakdownItem(BaseModel):
    """Breakdown por tipo de jogo"""
    label: str
    total: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0


class MonthlyData(BaseModel):
    """Dados mensais de jogos"""
    month: str  # "2025-01"
    label: str  # "Jan 2025"
    total: int = 0
    wins: int = 0
    losses: int = 0


class SurfaceStats(BaseModel):
    """Estatisticas por tipo de piso"""
    surface: str
    label: str
    total: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0


class AgeGroupStats(BaseModel):
    """Estatisticas por faixa etaria do oponente"""
    age_group: str  # "18-25", "26-35", etc.
    total: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0


class OpponentProfileStats(BaseModel):
    """Estatisticas vs perfil do oponente"""
    handedness: List[Dict[str, Any]] = []  # destro/canhoto
    backhand: List[Dict[str, Any]] = []  # 1 mao / 2 maos
    age_groups: List[AgeGroupStats] = []


class StreakItem(BaseModel):
    """Item de sequencia de resultados"""
    match_id: str
    date: str
    result: str  # "V" ou "D"
    opponent_name: str


class ResultTypeStats(BaseModel):
    """Estatisticas por tipo de resultado"""
    result_type: str  # "played", "wo", "withdrawal"
    label: str
    total: int = 0
    wins: int = 0
    losses: int = 0


class DashboardResponse(BaseModel):
    """Resposta completa do dashboard de estatisticas"""
    overall: OverallStats
    by_type: List[BreakdownItem] = []
    by_result_type: List[ResultTypeStats] = []
    monthly: List[MonthlyData] = []
    by_surface: List[SurfaceStats] = []
    opponent_profile: OpponentProfileStats = OpponentProfileStats()
    streak: List[StreakItem] = []
