"""
Computer Vision Detection - Módulos de Detecção

Implementa detecção de elementos do tênis:
- BallDetector: Detecção de bola usando TrackNet
- PlayerDetector: Detecção de jogadores usando YOLO/R-CNN
- CourtDetector: Detecção de linhas da quadra
- LineCaller: Detecção de bolas dentro/fora
"""

from .ball_detector import BallDetector
from .player_detector import PlayerDetector
from .court_detector import CourtDetector
from .line_caller import LineCaller

__all__ = ['BallDetector', 'PlayerDetector', 'CourtDetector', 'LineCaller']