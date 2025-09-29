"""
Analytics Module - Análises e Estatísticas

Fornece análises avançadas de partidas de tênis:
- Análise de desempenho
- Estatísticas detalhadas
- Mapas de calor
- Análise de movimentação
- Detecção de fadiga
"""

from .performance_analyzer import PerformanceAnalyzer
from .statistics_engine import StatisticsEngine
from .heatmap_generator import HeatmapGenerator
from .reports.match_report import MatchReport

__all__ = [
    'PerformanceAnalyzer',
    'StatisticsEngine',
    'HeatmapGenerator',
    'MatchReport'
]