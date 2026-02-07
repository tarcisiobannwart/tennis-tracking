"""
Tournament service - CRUD, search, registration management.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sql.tournament import (
    Tournament,
    TournamentCategory,
    TournamentRegistration,
    TournamentStatus,
    RegistrationStatus,
    PaymentStatus,
)
from app.models.tournament_schema import (
    TournamentCreate,
    TournamentUpdate,
    TournamentCategoryCreate,
    TournamentCategoryUpdate,
    TournamentRegistrationCreate,
)


class TournamentService:
    """Service para gerenciamento de torneios"""

    async def create_tournament(
        self, db: AsyncSession, organizer_id: uuid.UUID, data: TournamentCreate
    ) -> Tournament:
        """Criar um novo torneio"""
        tournament = Tournament(
            id=uuid.uuid4(),
            name=data.name,
            description=data.description,
            sport=data.sport,
            tournament_type=data.tournament_type,
            status=TournamentStatus.DRAFT,
            organizer_id=organizer_id,
            organization_id=uuid.UUID(data.organization_id) if data.organization_id else None,
            venue_name=data.venue_name,
            venue_address=data.venue_address,
            city=data.city,
            state=data.state,
            country=data.country,
            start_date=data.start_date,
            end_date=data.end_date,
            registration_start=data.registration_start,
            registration_deadline=data.registration_deadline,
            max_participants=data.max_participants,
            registration_fee=data.registration_fee,
            currency=data.currency,
            is_public=data.is_public,
            allow_waitlist=data.allow_waitlist,
            require_approval=data.require_approval,
            rules=data.rules,
            prizes=data.prizes,
            contact_info=data.contact_info,
            banner_image=data.banner_image,
            logo_image=data.logo_image,
        )
        db.add(tournament)
        await db.flush()
        await db.refresh(tournament)
        return tournament

    async def get_tournament_by_id(
        self, db: AsyncSession, tournament_id: uuid.UUID, include_categories: bool = False
    ) -> Optional[Tournament]:
        """Buscar torneio por ID"""
        query = select(Tournament).where(Tournament.id == tournament_id)
        if include_categories:
            query = query.options(selectinload(Tournament.categories))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_tournament(
        self, db: AsyncSession, tournament_id: uuid.UUID, organizer_id: uuid.UUID, data: TournamentUpdate
    ) -> Optional[Tournament]:
        """Atualizar torneio (apenas organizador)"""
        tournament = await self.get_tournament_by_id(db, tournament_id)
        if not tournament or tournament.organizer_id != organizer_id:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(tournament, key):
                setattr(tournament, key, value)

        await db.flush()
        await db.refresh(tournament)
        return tournament

    async def delete_tournament(
        self, db: AsyncSession, tournament_id: uuid.UUID, organizer_id: uuid.UUID
    ) -> bool:
        """Deletar torneio (apenas organizador)"""
        tournament = await self.get_tournament_by_id(db, tournament_id)
        if not tournament or tournament.organizer_id != organizer_id:
            return False

        await db.delete(tournament)
        await db.flush()
        return True

    async def search_tournaments(
        self,
        db: AsyncSession,
        sport: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        tournament_type: Optional[str] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None,
        is_public: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Tournament], int]:
        """Buscar torneios com filtros"""
        query = select(Tournament).where(Tournament.is_public == is_public)

        if sport:
            query = query.where(Tournament.sport == sport)
        if state:
            query = query.where(Tournament.state == state)
        if city:
            query = query.where(Tournament.city == city)
        if status:
            query = query.where(Tournament.status == status)
        if tournament_type:
            query = query.where(Tournament.tournament_type == tournament_type)
        if name:
            query = query.where(Tournament.name.ilike(f"%{name}%"))
        if start_date_from:
            query = query.where(Tournament.start_date >= start_date_from)
        if start_date_to:
            query = query.where(Tournament.start_date <= start_date_to)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Tournament.start_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        tournaments = result.scalars().all()

        return list(tournaments), total

    async def get_my_tournaments(
        self,
        db: AsyncSession,
        organizer_id: uuid.UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Tournament], int]:
        """Listar torneios criados pelo usuario"""
        query = select(Tournament).where(Tournament.organizer_id == organizer_id)

        if status:
            query = query.where(Tournament.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Tournament.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        tournaments = result.scalars().all()

        return list(tournaments), total

    async def add_category(
        self,
        db: AsyncSession,
        tournament_id: uuid.UUID,
        organizer_id: uuid.UUID,
        data: TournamentCategoryCreate,
    ) -> Optional[TournamentCategory]:
        """Adicionar categoria ao torneio"""
        tournament = await self.get_tournament_by_id(db, tournament_id)
        if not tournament or tournament.organizer_id != organizer_id:
            return None

        category = TournamentCategory(
            id=uuid.uuid4(),
            tournament_id=tournament_id,
            name=data.name,
            description=data.description,
            min_age=data.min_age,
            max_age=data.max_age,
            gender=data.gender,
            skill_level=data.skill_level,
            max_participants=data.max_participants,
            registration_fee=data.registration_fee,
        )
        db.add(category)
        await db.flush()
        await db.refresh(category)
        return category

    async def register_player(
        self,
        db: AsyncSession,
        tournament_id: uuid.UUID,
        player_id: uuid.UUID,
        data: TournamentRegistrationCreate,
    ) -> Optional[TournamentRegistration]:
        """Inscrever jogador no torneio"""
        tournament = await self.get_tournament_by_id(db, tournament_id)
        if not tournament or tournament.status != TournamentStatus.OPEN:
            return None

        existing = await db.execute(
            select(TournamentRegistration).where(
                TournamentRegistration.tournament_id == tournament_id,
                TournamentRegistration.player_id == player_id,
                TournamentRegistration.category_id == uuid.UUID(data.category_id),
            )
        )
        if existing.scalar_one_or_none():
            return None

        category = await db.execute(
            select(TournamentCategory).where(
                TournamentCategory.id == uuid.UUID(data.category_id)
            )
        )
        category_obj = category.scalar_one_or_none()
        if not category_obj:
            return None

        if category_obj.max_participants and category_obj.current_participants >= category_obj.max_participants:
            if not tournament.allow_waitlist:
                return None
            status = RegistrationStatus.WAITLIST
        else:
            status = RegistrationStatus.PENDING if tournament.registration_fee else RegistrationStatus.CONFIRMED

        registration = TournamentRegistration(
            id=uuid.uuid4(),
            tournament_id=tournament_id,
            category_id=uuid.UUID(data.category_id),
            player_id=player_id,
            player_name=data.player_name,
            player_email=data.player_email,
            player_phone=data.player_phone,
            player_document=data.player_document,
            partner_id=uuid.UUID(data.partner_id) if data.partner_id else None,
            partner_name=data.partner_name,
            team_name=data.team_name,
            notes=data.notes,
            emergency_contact=data.emergency_contact,
            medical_info=data.medical_info,
            status=status,
            payment_status=PaymentStatus.PENDING if tournament.registration_fee else PaymentStatus.PAID,
            amount_paid=category_obj.registration_fee or tournament.registration_fee,
        )
        db.add(registration)

        if status == RegistrationStatus.CONFIRMED:
            category_obj.current_participants += 1
            tournament.current_participants += 1

        await db.flush()
        await db.refresh(registration)
        return registration

    async def get_player_registrations(
        self, db: AsyncSession, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> List[TournamentRegistration]:
        """Listar inscricoes do jogador"""
        query = (
            select(TournamentRegistration)
            .where(TournamentRegistration.player_id == player_id)
            .order_by(TournamentRegistration.registered_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def cancel_registration(
        self, db: AsyncSession, registration_id: uuid.UUID, player_id: uuid.UUID
    ) -> bool:
        """Cancelar inscricao"""
        result = await db.execute(
            select(TournamentRegistration).where(
                TournamentRegistration.id == registration_id,
                TournamentRegistration.player_id == player_id,
            )
        )
        registration = result.scalar_one_or_none()
        if not registration:
            return False

        registration.status = RegistrationStatus.CANCELLED
        await db.flush()
        return True
