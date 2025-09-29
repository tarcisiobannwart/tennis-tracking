"""
Computer Vision Tracking - M�dulos de Rastreamento

Implementa algoritmos de rastreamento de objetos:
- ObjectTracker: Rastreamento gen�rico de objetos
- SORT: Simple Online and Realtime Tracking
- PlayerTracker: Rastreamento espec�fico de jogadores
"""

try:
    from .object_tracker import ObjectTracker
    __all__ = ['ObjectTracker']
except ImportError:
    # Fallback se object_tracker n�o existir ainda
    __all__ = []