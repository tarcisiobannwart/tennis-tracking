"""
Computer Vision Module - Visão Computacional

Módulo base para detecção e rastreamento usando visão computacional:
- Detecção de bola, jogadores e quadra
- Rastreamento de objetos
- Análise de trajetória
- Cálculo de velocidade
"""

from .detection.ball_detector import BallDetector
from .detection.player_detector import PlayerDetector
from .detection.court_detector import CourtDetector
from .tracking.object_tracker import ObjectTracker
from .models.tracknet import TrackNet

__all__ = [
    'BallDetector',
    'PlayerDetector',
    'CourtDetector',
    'ObjectTracker',
    'TrackNet'
]