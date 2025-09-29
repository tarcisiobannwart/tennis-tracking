"""
Computer Vision Tracking - Módulos de Rastreamento

Implementa algoritmos de rastreamento de objetos:
- ObjectTracker: Rastreamento genérico de objetos
- SORT: Simple Online and Realtime Tracking
- PlayerTracker: Rastreamento específico de jogadores
"""

try:
    from .object_tracker import ObjectTracker
    __all__ = ['ObjectTracker']
except ImportError:
    # Fallback se object_tracker não existir ainda
    __all__ = []