"""
Pydantic schemas para Tournament API (request/response DTOs).

Seguem o padrao Base → Create → Update → Response.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================
# Tournament Schemas
# ============================================================

class TournamentBase(BaseModel):
    """Base schema para Tournament"""
    name: str
    description: Optional[str] = None
    sport: str = "tennis"
    tournament_type: str = "singles"
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Brazil"
    start_date: datetime
    end_date: datetime
    registration_start: datetime
    registration_deadline: datetime
    max_participants: Optional[int] = None
    registration_fee: Optional[float] = None
    currency: str = "BRL"
    is_public: bool = True
    allow_waitlist: bool = False
    require_approval: bool = False
    rules: Optional[str] = None
    prizes: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    banner_image: Optional[str] = None
    logo_image: Optional[str] = None


class TournamentCreate(TournamentBase):
    """Schema para criar torneio"""
    organization_id: Optional[str] = None


class TournamentUpdate(BaseModel):
    """Schema para atualizar torneio"""
    name: Optional[str] = None
    description: Optional[str] = None
    tournament_type: Optional[str] = None
    status: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_start: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    max_participants: Optional[int] = None
    registration_fee: Optional[float] = None
    is_public: Optional[bool] = None
    allow_waitlist: Optional[bool] = None
    require_approval: Optional[bool] = None
    rules: Optional[str] = None
    prizes: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    banner_image: Optional[str] = None
    logo_image: Optional[str] = None


class TournamentResponse(TournamentBase):
    """Schema de resposta para Tournament"""
    id: str
    status: str
    organizer_id: str
    organization_id: Optional[str] = None
    current_participants: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TournamentDetailResponse(TournamentResponse):
    """Schema detalhado com categorias"""
    categories: List["TournamentCategoryResponse"] = []


# ============================================================
# TournamentCategory Schemas
# ============================================================

class TournamentCategoryBase(BaseModel):
    """Base schema para TournamentCategory"""
    name: str
    description: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = None
    skill_level: Optional[str] = None
    max_participants: Optional[int] = None
    registration_fee: Optional[float] = None


class TournamentCategoryCreate(TournamentCategoryBase):
    """Schema para criar categoria"""
    pass


class TournamentCategoryUpdate(BaseModel):
    """Schema para atualizar categoria"""
    name: Optional[str] = None
    description: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = None
    skill_level: Optional[str] = None
    max_participants: Optional[int] = None
    registration_fee: Optional[float] = None


class TournamentCategoryResponse(TournamentCategoryBase):
    """Schema de resposta para TournamentCategory"""
    id: str
    tournament_id: str
    current_participants: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# TournamentRegistration Schemas
# ============================================================

class TournamentRegistrationBase(BaseModel):
    """Base schema para TournamentRegistration"""
    player_name: str
    player_email: str
    player_phone: Optional[str] = None
    player_document: Optional[str] = None
    partner_id: Optional[str] = None
    partner_name: Optional[str] = None
    team_name: Optional[str] = None
    notes: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    medical_info: Optional[str] = None


class TournamentRegistrationCreate(TournamentRegistrationBase):
    """Schema para criar inscricao"""
    category_id: str


class TournamentRegistrationUpdate(BaseModel):
    """Schema para atualizar inscricao"""
    status: Optional[str] = None
    player_phone: Optional[str] = None
    notes: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    medical_info: Optional[str] = None


class TournamentRegistrationResponse(TournamentRegistrationBase):
    """Schema de resposta para TournamentRegistration"""
    id: str
    tournament_id: str
    category_id: str
    player_id: str
    status: str
    payment_status: str
    amount_paid: Optional[float] = None
    payment_method: Optional[str] = None
    paid_at: Optional[datetime] = None
    registered_at: datetime
    confirmed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Search/Filter Schemas
# ============================================================

class TournamentSearchFilters(BaseModel):
    """Filtros para busca de torneios"""
    sport: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    name: Optional[str] = None
    status: Optional[str] = None
    tournament_type: Optional[str] = None
    is_public: bool = True


class TournamentListResponse(BaseModel):
    """Resposta paginada de torneios"""
    total: int
    tournaments: List[TournamentResponse]


# Resolver forward references para TournamentDetailResponse
TournamentDetailResponse.model_rebuild()
