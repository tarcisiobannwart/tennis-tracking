"""
Scoring Module - Sistema de Pontuação

Implementa o sistema oficial de pontuação do tênis:
- Regras ATP/WTA
- Gestão de tie-breaks
- Sistema de vantagens
- Histórico de pontos
"""

from .score_manager import ScoreManager
from .point_tracker import PointTracker
from .models.scoreboard import Scoreboard
from .models.point_history import PointHistory

__all__ = [
    'ScoreManager',
    'PointTracker',
    'Scoreboard',
    'PointHistory'
]