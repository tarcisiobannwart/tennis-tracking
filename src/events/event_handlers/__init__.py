"""
Event Handlers - Manipuladores de Eventos

Handlers especializados para diferentes tipos de eventos:
- AceHandler: Eventos de ace
- FaultHandler: Eventos de falta
- WinnerHandler: Eventos de winner
- ErrorHandler: Eventos de erro não forçado
"""

from .ace_handler import AceHandler
from .fault_handler import FaultHandler
from .winner_handler import WinnerHandler
from .error_handler import ErrorHandler

__all__ = ['AceHandler', 'FaultHandler', 'WinnerHandler', 'ErrorHandler']