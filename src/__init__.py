"""
Tennis Analytics - Sistema de Análise de Tênis

Sistema completo para análise de vídeos de tênis usando visão computacional
e inteligência artificial. Fornece análises em tempo real de partidas,
estatísticas detalhadas e insights táticos.

Nova Arquitetura Orientada ao Domínio:
- game_control: Controle de jogos e partidas
- scoring: Sistema de pontuação ATP/WTA
- analytics: Análises e estatísticas avançadas
- computer_vision: Detecção e rastreamento
- events: Sistema de eventos em tempo real
- api: Interface REST e WebSocket
"""

__version__ = "2.0.0"
__author__ = "Tennis Analytics Team"

# Importações principais para compatibilidade
from .app import TennisAnalyticsApp

__all__ = [
    'TennisAnalyticsApp'
]