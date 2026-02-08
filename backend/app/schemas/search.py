"""
Schemas Pydantic para busca global.

Implementado para TT-138: Busca global de jogadores, locais, rankings e torneios.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PlayerSearchResult(BaseModel):
    """Resultado de busca de jogador."""
    id: UUID
    name: str
    avatar_url: Optional[str]
    username: str

    class Config:
        from_attributes = True


class VenueSearchResult(BaseModel):
    """Resultado de busca de local/clube/academia."""
    id: UUID
    name: str
    city: Optional[str]
    type: str

    class Config:
        from_attributes = True


class RankingSearchResult(BaseModel):
    """Resultado de busca de ranking."""
    id: UUID
    name: str
    category: Optional[str]

    class Config:
        from_attributes = True


class TournamentSearchResult(BaseModel):
    """Resultado de busca de torneio."""
    id: UUID
    name: str
    date: Optional[str]
    status: str

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Resposta de busca global agrupada por categoria."""
    players: list[PlayerSearchResult]
    venues: list[VenueSearchResult]
    rankings: list[RankingSearchResult]
    tournaments: list[TournamentSearchResult]
