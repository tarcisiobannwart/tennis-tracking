"""
Tournament API routes - CRUD, search, registration.
"""

import uuid
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.sql.tournament import TournamentStatus
from app.models.tournament_schema import (
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
    TournamentDetailResponse,
    TournamentListResponse,
    TournamentCategoryCreate,
    TournamentCategoryResponse,
    TournamentRegistrationCreate,
    TournamentRegistrationResponse,
)
from app.services.tournament_service import TournamentService

router = APIRouter()
logger = structlog.get_logger(__name__)
tournament_service = TournamentService()


def to_tournament_response(t) -> TournamentResponse:
    """Converter Tournament ORM para TournamentResponse"""
    return TournamentResponse(
        id=str(t.id),
        name=t.name,
        description=t.description,
        sport=t.sport,
        tournament_type=t.tournament_type,
        status=t.status,
        organizer_id=str(t.organizer_id),
        organization_id=str(t.organization_id) if t.organization_id else None,
        venue_name=t.venue_name,
        venue_address=t.venue_address,
        city=t.city,
        state=t.state,
        country=t.country,
        start_date=t.start_date,
        end_date=t.end_date,
        registration_start=t.registration_start,
        registration_deadline=t.registration_deadline,
        max_participants=t.max_participants,
        current_participants=t.current_participants,
        registration_fee=t.registration_fee,
        currency=t.currency,
        is_public=t.is_public,
        allow_waitlist=t.allow_waitlist,
        require_approval=t.require_approval,
        rules=t.rules,
        prizes=t.prizes,
        contact_info=t.contact_info,
        banner_image=t.banner_image,
        logo_image=t.logo_image,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.post("/", response_model=TournamentResponse, status_code=201)
async def create_tournament(
    data: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Criar novo torneio"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    tournament = await tournament_service.create_tournament(db, user_id, data)
    return to_tournament_response(tournament)


@router.get("/{tournament_id}", response_model=TournamentDetailResponse)
async def get_tournament(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Buscar torneio por ID com categorias"""
    tournament = await tournament_service.get_tournament_by_id(
        db, uuid.UUID(tournament_id), include_categories=True
    )
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    categories = [
        TournamentCategoryResponse(
            id=str(cat.id),
            tournament_id=str(cat.tournament_id),
            name=cat.name,
            description=cat.description,
            min_age=cat.min_age,
            max_age=cat.max_age,
            gender=cat.gender,
            skill_level=cat.skill_level,
            max_participants=cat.max_participants,
            current_participants=cat.current_participants,
            registration_fee=cat.registration_fee,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
        )
        for cat in tournament.categories
    ]

    return TournamentDetailResponse(
        id=str(tournament.id),
        name=tournament.name,
        description=tournament.description,
        sport=tournament.sport,
        tournament_type=tournament.tournament_type,
        status=tournament.status,
        organizer_id=str(tournament.organizer_id),
        organization_id=str(tournament.organization_id) if tournament.organization_id else None,
        venue_name=tournament.venue_name,
        venue_address=tournament.venue_address,
        city=tournament.city,
        state=tournament.state,
        country=tournament.country,
        start_date=tournament.start_date,
        end_date=tournament.end_date,
        registration_start=tournament.registration_start,
        registration_deadline=tournament.registration_deadline,
        max_participants=tournament.max_participants,
        current_participants=tournament.current_participants,
        registration_fee=tournament.registration_fee,
        currency=tournament.currency,
        is_public=tournament.is_public,
        allow_waitlist=tournament.allow_waitlist,
        require_approval=tournament.require_approval,
        rules=tournament.rules,
        prizes=tournament.prizes,
        contact_info=tournament.contact_info,
        banner_image=tournament.banner_image,
        logo_image=tournament.logo_image,
        created_at=tournament.created_at,
        updated_at=tournament.updated_at,
        categories=categories,
    )


@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: str,
    data: TournamentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Atualizar torneio (apenas organizador)"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    tournament = await tournament_service.update_tournament(
        db, uuid.UUID(tournament_id), user_id, data
    )
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found or unauthorized")

    return to_tournament_response(tournament)


@router.delete("/{tournament_id}", status_code=204)
async def delete_tournament(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Deletar torneio (apenas organizador)"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    success = await tournament_service.delete_tournament(
        db, uuid.UUID(tournament_id), user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Tournament not found or unauthorized")
    return None


@router.get("/", response_model=TournamentListResponse)
async def search_tournaments(
    sport: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tournament_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Buscar torneios abertos com filtros"""
    tournaments, total = await tournament_service.search_tournaments(
        db,
        sport=sport,
        state=state,
        city=city,
        name=name,
        status=status or TournamentStatus.OPEN.value,
        tournament_type=tournament_type,
        is_public=True,
        skip=skip,
        limit=limit,
    )

    tournament_responses = [to_tournament_response(t) for t in tournaments]
    return TournamentListResponse(total=total, tournaments=tournament_responses)


@router.get("/my/tournaments", response_model=TournamentListResponse)
async def get_my_tournaments(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Listar meus torneios (organizados por mim)"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    tournaments, total = await tournament_service.get_my_tournaments(
        db, user_id, status=status, skip=skip, limit=limit
    )

    tournament_responses = [to_tournament_response(t) for t in tournaments]
    return TournamentListResponse(total=total, tournaments=tournament_responses)


@router.post("/{tournament_id}/categories", response_model=TournamentCategoryResponse, status_code=201)
async def add_category(
    tournament_id: str,
    data: TournamentCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Adicionar categoria ao torneio"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    category = await tournament_service.add_category(
        db, uuid.UUID(tournament_id), user_id, data
    )
    if not category:
        raise HTTPException(status_code=404, detail="Tournament not found or unauthorized")

    return TournamentCategoryResponse(
        id=str(category.id),
        tournament_id=str(category.tournament_id),
        name=category.name,
        description=category.description,
        min_age=category.min_age,
        max_age=category.max_age,
        gender=category.gender,
        skill_level=category.skill_level,
        max_participants=category.max_participants,
        current_participants=category.current_participants,
        registration_fee=category.registration_fee,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


@router.post("/{tournament_id}/register", response_model=TournamentRegistrationResponse, status_code=201)
async def register_for_tournament(
    tournament_id: str,
    data: TournamentRegistrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Inscrever-se em um torneio"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    registration = await tournament_service.register_player(
        db, uuid.UUID(tournament_id), user_id, data
    )
    if not registration:
        raise HTTPException(
            status_code=400,
            detail="Unable to register. Tournament may be full or not accepting registrations.",
        )

    return TournamentRegistrationResponse(
        id=str(registration.id),
        tournament_id=str(registration.tournament_id),
        category_id=str(registration.category_id),
        player_id=str(registration.player_id),
        player_name=registration.player_name,
        player_email=registration.player_email,
        player_phone=registration.player_phone,
        player_document=registration.player_document,
        partner_id=str(registration.partner_id) if registration.partner_id else None,
        partner_name=registration.partner_name,
        team_name=registration.team_name,
        status=registration.status,
        payment_status=registration.payment_status,
        amount_paid=registration.amount_paid,
        payment_method=registration.payment_method,
        paid_at=registration.paid_at,
        notes=registration.notes,
        emergency_contact=registration.emergency_contact,
        medical_info=registration.medical_info,
        registered_at=registration.registered_at,
        confirmed_at=registration.confirmed_at,
        updated_at=registration.updated_at,
    )


@router.get("/my/registrations", response_model=list[TournamentRegistrationResponse])
async def get_my_registrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Listar minhas inscricoes"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    registrations = await tournament_service.get_player_registrations(
        db, user_id, skip=skip, limit=limit
    )

    return [
        TournamentRegistrationResponse(
            id=str(r.id),
            tournament_id=str(r.tournament_id),
            category_id=str(r.category_id),
            player_id=str(r.player_id),
            player_name=r.player_name,
            player_email=r.player_email,
            player_phone=r.player_phone,
            player_document=r.player_document,
            partner_id=str(r.partner_id) if r.partner_id else None,
            partner_name=r.partner_name,
            team_name=r.team_name,
            status=r.status,
            payment_status=r.payment_status,
            amount_paid=r.amount_paid,
            payment_method=r.payment_method,
            paid_at=r.paid_at,
            notes=r.notes,
            emergency_contact=r.emergency_contact,
            medical_info=r.medical_info,
            registered_at=r.registered_at,
            confirmed_at=r.confirmed_at,
            updated_at=r.updated_at,
        )
        for r in registrations
    ]


@router.delete("/registrations/{registration_id}", status_code=204)
async def cancel_registration(
    registration_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cancelar inscricao"""
    user_id = uuid.UUID(current_user.get("id") or current_user.get("_id"))
    success = await tournament_service.cancel_registration(
        db, uuid.UUID(registration_id), user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Registration not found or unauthorized")
    return None
