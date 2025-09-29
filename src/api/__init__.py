"""
API Module - Interface REST e WebSocket

Fornece APIs para acesso aos dados de tênis:
- REST API para dados históricos
- WebSocket para dados em tempo real
- Rotas para partidas, jogadores e análises
"""

from .app import create_app
from .routes.match_routes import match_router
from .routes.player_routes import player_router
from .routes.analytics_routes import analytics_router

__all__ = [
    'create_app',
    'match_router',
    'player_router',
    'analytics_router'
]