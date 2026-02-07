"""
Venues API routes - locais/clubes management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import UserInDB
from app.models.sql.venue import Venue, VenueMember
from app.services.venue_service import venue_service

router = APIRouter()


# --- Pydantic Schemas ---

class VenueCreate(BaseModel):
    """Schema for creating a venue"""
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    sport_types: list[str] = ["tennis"]
    court_count: int = 0
    surface_types: list[str] = []
    amenities: list[str] = []
    is_public: bool = True


class VenueUpdate(BaseModel):
    """Schema for updating a venue"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    sport_types: Optional[list[str]] = None
    court_count: Optional[int] = None
    surface_types: Optional[list[str]] = None
    amenities: Optional[list[str]] = None
    is_public: Optional[bool] = None


class VenueResponse(BaseModel):
    """Schema for venue response"""
    id: str
    name: str
    slug: str
    description: Optional[str]
    avatar_url: Optional[str]
    cover_photo_url: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    sport_types: list[str]
    court_count: int
    surface_types: list[str]
    amenities: list[str]
    followers_count: int
    members_count: int
    is_public: bool
    owner_id: str
    created_at: str
    updated_at: str
    is_following: bool = False
    is_member: bool = False
    member_role: Optional[str] = None

    class Config:
        from_attributes = True


class VenueListResponse(BaseModel):
    """Schema for venue list response"""
    venues: list[VenueResponse]
    total: int
    skip: int
    limit: int


# --- Helper Functions ---

def _build_venue_response(venue: Venue, is_following: bool = False, is_member: bool = False, member_role: Optional[str] = None) -> VenueResponse:
    """Build VenueResponse from Venue SQLAlchemy object"""
    return VenueResponse(
        id=str(venue.id),
        name=venue.name,
        slug=venue.slug,
        description=venue.description,
        avatar_url=venue.avatar_url,
        cover_photo_url=venue.cover_photo_url,
        address=venue.address,
        city=venue.city,
        state=venue.state,
        country=venue.country,
        latitude=venue.latitude,
        longitude=venue.longitude,
        phone=venue.phone,
        email=venue.email,
        website=venue.website,
        sport_types=venue.sport_types or [],
        court_count=venue.court_count,
        surface_types=venue.surface_types or [],
        amenities=venue.amenities or [],
        followers_count=venue.followers_count,
        members_count=venue.members_count,
        is_public=venue.is_public,
        owner_id=str(venue.owner_id),
        created_at=venue.created_at.isoformat(),
        updated_at=venue.updated_at.isoformat(),
        is_following=is_following,
        is_member=is_member,
        member_role=member_role,
    )


# --- Routes ---

@router.get("", response_model=VenueListResponse)
async def list_venues(
    skip: int = 0,
    limit: int = 20,
    city: Optional[str] = None,
    country: Optional[str] = None,
    sport: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserInDB] = Depends(get_current_active_user),
):
    """List venues with filters"""
    venues, total = await venue_service.list_venues(
        db,
        skip=skip,
        limit=limit,
        city=city,
        country=country,
        sport=sport,
        search=search,
        is_public=True,
    )

    # Build responses with user-specific flags
    venue_responses = []
    for venue in venues:
        is_following = False
        is_member = False
        member_role = None
        if current_user:
            user_uuid = uuid.UUID(current_user.id)
            is_following = await venue_service.is_following(db, venue.id, user_uuid)
            is_member = await venue_service.is_member(db, venue.id, user_uuid)
            if is_member:
                member_role = await venue_service.get_member_role(db, venue.id, user_uuid)
        venue_responses.append(_build_venue_response(venue, is_following, is_member, member_role))

    return VenueListResponse(
        venues=venue_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{slug}", response_model=VenueResponse)
async def get_venue(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserInDB] = Depends(get_current_active_user),
):
    """Get venue by slug"""
    venue = await venue_service.get_by_slug(db, slug)
    if not venue:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    # Check user-specific flags
    is_following = False
    is_member = False
    member_role = None
    if current_user:
        user_uuid = uuid.UUID(current_user.id)
        is_following = await venue_service.is_following(db, venue.id, user_uuid)
        is_member = await venue_service.is_member(db, venue.id, user_uuid)
        if is_member:
            member_role = await venue_service.get_member_role(db, venue.id, user_uuid)

    return _build_venue_response(venue, is_following, is_member, member_role)


@router.post("", response_model=VenueResponse)
async def create_venue(
    venue_data: VenueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Create new venue"""
    owner_uuid = uuid.UUID(current_user.id)
    venue = await venue_service.create(db, venue_data.dict(), owner_uuid)
    await db.commit()

    # Owner is member by default
    return _build_venue_response(venue, is_following=False, is_member=True, member_role="owner")


@router.put("/{venue_id}", response_model=VenueResponse)
async def update_venue(
    venue_id: str,
    update_data: VenueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Update venue (only owner/admin can update)"""
    try:
        venue_uuid = uuid.UUID(venue_id)
        user_uuid = uuid.UUID(current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Check if user is owner or admin
    member_role = await venue_service.get_member_role(db, venue_uuid, user_uuid)
    if member_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Sem permissão para editar este local")

    venue = await venue_service.update(db, venue_uuid, update_data.dict(exclude_unset=True))
    if not venue:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    await db.commit()

    is_following = await venue_service.is_following(db, venue_uuid, user_uuid)
    is_member = await venue_service.is_member(db, venue_uuid, user_uuid)

    return _build_venue_response(venue, is_following, is_member, member_role)


@router.delete("/{venue_id}")
async def delete_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Delete venue (only owner can delete)"""
    try:
        venue_uuid = uuid.UUID(venue_id)
        user_uuid = uuid.UUID(current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Check if user is owner
    member_role = await venue_service.get_member_role(db, venue_uuid, user_uuid)
    if member_role != "owner":
        raise HTTPException(status_code=403, detail="Apenas o dono pode deletar este local")

    success = await venue_service.delete(db, venue_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    await db.commit()
    return {"message": "Local deletado com sucesso"}


@router.post("/{venue_id}/follow")
async def follow_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Follow a venue"""
    try:
        venue_uuid = uuid.UUID(venue_id)
        user_uuid = uuid.UUID(current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Check if venue exists
    venue = await venue_service.get_by_id(db, venue_uuid)
    if not venue:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    success = await venue_service.follow(db, venue_uuid, user_uuid)
    if not success:
        raise HTTPException(status_code=400, detail="Você já segue este local")

    await db.commit()
    return {"message": "Você agora segue este local"}


@router.post("/{venue_id}/unfollow")
async def unfollow_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Unfollow a venue"""
    try:
        venue_uuid = uuid.UUID(venue_id)
        user_uuid = uuid.UUID(current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    success = await venue_service.unfollow(db, venue_uuid, user_uuid)
    if not success:
        raise HTTPException(status_code=400, detail="Você não segue este local")

    await db.commit()
    return {"message": "Você deixou de seguir este local"}


@router.post("/{venue_id}/join")
async def join_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Join a venue as member"""
    try:
        venue_uuid = uuid.UUID(venue_id)
        user_uuid = uuid.UUID(current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Check if venue exists
    venue = await venue_service.get_by_id(db, venue_uuid)
    if not venue:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    success = await venue_service.join(db, venue_uuid, user_uuid)
    if not success:
        raise HTTPException(status_code=400, detail="Você já é membro deste local")

    await db.commit()
    return {"message": "Você agora é membro deste local"}


@router.post("/{venue_id}/leave")
async def leave_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Leave a venue (only non-owners)"""
    try:
        venue_uuid = uuid.UUID(venue_id)
        user_uuid = uuid.UUID(current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    success = await venue_service.leave(db, venue_uuid, user_uuid)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Você não é membro ou é o dono (donos não podem sair)"
        )

    await db.commit()
    return {"message": "Você saiu deste local"}


@router.get("/{venue_id}/members")
async def get_venue_members(
    venue_id: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserInDB] = Depends(get_current_active_user),
):
    """Get venue members list"""
    try:
        venue_uuid = uuid.UUID(venue_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Check if venue exists
    venue = await venue_service.get_by_id(db, venue_uuid)
    if not venue:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    members, total = await venue_service.get_venue_members(db, venue_uuid, skip, limit)

    return {
        "members": [
            {
                "user_id": str(member.user_id),
                "role": member.role,
                "joined_at": member.joined_at.isoformat(),
            }
            for member in members
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{venue_id}/followers")
async def get_venue_followers(
    venue_id: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserInDB] = Depends(get_current_active_user),
):
    """Get venue followers list"""
    try:
        venue_uuid = uuid.UUID(venue_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Check if venue exists
    venue = await venue_service.get_by_id(db, venue_uuid)
    if not venue:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    followers, total = await venue_service.get_venue_followers(db, venue_uuid, skip, limit)

    return {
        "followers": [
            {
                "user_id": str(follower.user_id),
                "followed_at": follower.followed_at.isoformat(),
            }
            for follower in followers
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
