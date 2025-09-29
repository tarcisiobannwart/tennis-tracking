"""
Scoring Models - Modelos de Dados da Pontuação

Define estruturas para rastreamento de pontuação:
- Scoreboard: Estado atual do placar
- PointHistory: Histórico completo de pontos
"""

from .scoreboard import Scoreboard
from .point_history import PointHistory

__all__ = ['Scoreboard', 'PointHistory']