"""
Computer Vision Models - Modelos de Visão Computacional

Contém os modelos de machine learning para análise de vídeos de tênis:
- TrackNet: Modelo para detecção de bola
- YOLO: Wrapper para detecção de objetos
"""

from .tracknet import trackNet

__all__ = ['trackNet']