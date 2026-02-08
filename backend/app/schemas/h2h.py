"""
H2H (Head to Head) Pydantic schemas - TT-134
Schemas para comparativo H2H entre jogadores
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class PlayerProfile(BaseModel):
    """Perfil basico do jogador para H2H"""
    id: str
    name: str
    avatar_url: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    dominant_hand: Optional[str] = None
    country: Optional[str] = None
    ranking: Optional[int] = None
    skill_level: Optional[str] = None


class H2HScore(BaseModel):
    """Placar H2H"""
    player_wins: int = 0
    opponent_wins: int = 0


class ComparisonItem(BaseModel):
    """Item de comparacao entre jogadores"""
    attribute: str
    label: str
    player_value: Optional[str] = None
    opponent_value: Optional[str] = None


class H2HMatchItem(BaseModel):
    """Item de historico de confronto"""
    match_id: str
    date: Optional[str] = None
    result: str  # "win" ou "loss" (perspectiva do player)
    player_sets: int = 0
    opponent_sets: int = 0
    sets_detail: List[Dict[str, Any]] = []
    tournament: Optional[str] = None
    surface: Optional[str] = None
    venue: Optional[str] = None
    duration_minutes: Optional[int] = None


class SetsGamesOverTime(BaseModel):
    """Sets e games disputados ao longo do tempo"""
    match_date: str
    match_label: str  # "vs Oponente - Jan 2025"
    player_sets: int = 0
    opponent_sets: int = 0
    player_games: int = 0
    opponent_games: int = 0


class H2HResponse(BaseModel):
    """Resposta completa do H2H"""
    player: PlayerProfile
    opponent: PlayerProfile
    h2h_score: H2HScore
    comparison: List[ComparisonItem] = []
    sets_games_over_time: List[SetsGamesOverTime] = []
    match_history: List[H2HMatchItem] = []
    total_matches: int = 0
    total_sets_player: int = 0
    total_sets_opponent: int = 0
    total_games_player: int = 0
    total_games_opponent: int = 0


class OpponentSummary(BaseModel):
    """Resumo de adversario para lista de oponentes"""
    id: str
    name: str
    avatar_url: Optional[str] = None
    total_matches: int = 0
    player_wins: int = 0
    opponent_wins: int = 0
    last_match_date: Optional[str] = None
