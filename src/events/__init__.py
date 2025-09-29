"""
Events Module - Sistema de Eventos

Gerencia eventos de tênis em tempo real:
- Detecção de aces, winners, erros
- Break points e match points
- Sistema de notificações
- Marcos importantes da partida
"""

from .event_manager import EventManager
from .event_types import EventTypes
from .notifications.alert_system import AlertSystem

__all__ = [
    'EventManager',
    'EventTypes',
    'AlertSystem'
]