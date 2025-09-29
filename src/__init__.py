"""
Tennis Analytics - Sistema de An�lise de T�nis

Sistema completo para an�lise de v�deos de t�nis usando vis�o computacional
e intelig�ncia artificial. Fornece an�lises em tempo real de partidas,
estat�sticas detalhadas e insights t�ticos.

Nova Arquitetura Orientada ao Dom�nio:
- game_control: Controle de jogos e partidas
- scoring: Sistema de pontua��o ATP/WTA
- analytics: An�lises e estat�sticas avan�adas
- computer_vision: Detec��o e rastreamento
- events: Sistema de eventos em tempo real
- api: Interface REST e WebSocket
"""

__version__ = "2.0.0"
__author__ = "Tennis Analytics Team"

# Importa��es principais para compatibilidade
from .app import TennisAnalyticsApp

__all__ = [
    'TennisAnalyticsApp'
]