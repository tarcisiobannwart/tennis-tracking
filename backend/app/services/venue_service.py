"""
Venue service - CRUD, follow/unfollow, join/leave, stats
"""
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.models.sql.venue import Venue, VenueMember, VenueFollower, VenueMemberRole


class VenueService:
    """Service for venue (local/clube) management"""

    async def get_by_id(self, db: AsyncSession, venue_id: uuid.UUID) -> Optional[Venue]:
        """Get venue by ID"""
        result = await db.execute(
            select(Venue).where(Venue.id == venue_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Venue]:
        """Get venue by slug"""
        result = await db.execute(
            select(Venue).where(Venue.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, venue_data: dict, owner_id: uuid.UUID) -> Venue:
        """Create new venue"""
        # Generate unique slug
        base_slug = slugify(venue_data.get("name", "venue"))
        slug = base_slug
        counter = 1
        while await self.get_by_slug(db, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        venue = Venue(
            id=uuid.uuid4(),
            name=venue_data["name"],
            slug=slug,
            description=venue_data.get("description"),
            avatar_url=venue_data.get("avatar_url"),
            cover_photo_url=venue_data.get("cover_photo_url"),
            address=venue_data.get("address"),
            city=venue_data.get("city"),
            state=venue_data.get("state"),
            country=venue_data.get("country"),
            latitude=venue_data.get("latitude"),
            longitude=venue_data.get("longitude"),
            phone=venue_data.get("phone"),
            email=venue_data.get("email"),
            website=venue_data.get("website"),
            sport_types=venue_data.get("sport_types", ["tennis"]),
            court_count=venue_data.get("court_count", 0),
            surface_types=venue_data.get("surface_types", []),
            amenities=venue_data.get("amenities", []),
            is_public=venue_data.get("is_public", True),
            owner_id=owner_id,
            followers_count=0,
            members_count=1,  # Owner is first member
        )
        db.add(venue)
        await db.flush()

        # Add owner as OWNER member
        owner_member = VenueMember(
            id=uuid.uuid4(),
            venue_id=venue.id,
            user_id=owner_id,
            role=VenueMemberRole.OWNER,
        )
        db.add(owner_member)
        await db.flush()

        await db.refresh(venue)
        return venue

    async def update(self, db: AsyncSession, venue_id: uuid.UUID, update_data: dict) -> Optional[Venue]:
        """Update venue"""
        venue = await self.get_by_id(db, venue_id)
        if not venue:
            return None

        for key, value in update_data.items():
            if hasattr(venue, key) and key not in ["id", "slug", "owner_id", "created_at"]:
                setattr(venue, key, value)

        venue.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(venue)
        return venue

    async def delete(self, db: AsyncSession, venue_id: uuid.UUID) -> bool:
        """Delete venue (only owner can delete)"""
        venue = await self.get_by_id(db, venue_id)
        if not venue:
            return False

        await db.delete(venue)
        await db.flush()
        return True

    async def list_venues(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        city: Optional[str] = None,
        country: Optional[str] = None,
        sport: Optional[str] = None,
        search: Optional[str] = None,
        is_public: bool = True,
    ) -> tuple[list[Venue], int]:
        """List venues with filters"""
        query = select(Venue).where(Venue.is_public == is_public)

        if city:
            query = query.where(Venue.city.ilike(f"%{city}%"))
        if country:
            query = query.where(Venue.country.ilike(f"%{country}%"))
        if sport:
            # JSONB contains check
            query = query.where(Venue.sport_types.contains([sport]))
        if search:
            query = query.where(
                or_(
                    Venue.name.ilike(f"%{search}%"),
                    Venue.city.ilike(f"%{search}%"),
                    Venue.description.ilike(f"%{search}%"),
                )
            )

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginated results
        query = query.order_by(Venue.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        venues = result.scalars().all()

        return list(venues), total

    # --- Follow/Unfollow ---

    async def follow(self, db: AsyncSession, venue_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Follow a venue"""
        # Check if already following
        existing = await db.execute(
            select(VenueFollower).where(
                and_(
                    VenueFollower.venue_id == venue_id,
                    VenueFollower.user_id == user_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            return False  # Already following

        follower = VenueFollower(
            id=uuid.uuid4(),
            venue_id=venue_id,
            user_id=user_id,
        )
        db.add(follower)

        # Increment followers_count
        venue = await self.get_by_id(db, venue_id)
        if venue:
            venue.followers_count += 1

        await db.flush()
        return True

    async def unfollow(self, db: AsyncSession, venue_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Unfollow a venue"""
        result = await db.execute(
            select(VenueFollower).where(
                and_(
                    VenueFollower.venue_id == venue_id,
                    VenueFollower.user_id == user_id,
                )
            )
        )
        follower = result.scalar_one_or_none()
        if not follower:
            return False

        await db.delete(follower)

        # Decrement followers_count
        venue = await self.get_by_id(db, venue_id)
        if venue and venue.followers_count > 0:
            venue.followers_count -= 1

        await db.flush()
        return True

    async def is_following(self, db: AsyncSession, venue_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is following venue"""
        result = await db.execute(
            select(VenueFollower).where(
                and_(
                    VenueFollower.venue_id == venue_id,
                    VenueFollower.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    # --- Join/Leave (membership) ---

    async def join(self, db: AsyncSession, venue_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Join a venue as member"""
        # Check if already member
        existing = await db.execute(
            select(VenueMember).where(
                and_(
                    VenueMember.venue_id == venue_id,
                    VenueMember.user_id == user_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            return False  # Already member

        member = VenueMember(
            id=uuid.uuid4(),
            venue_id=venue_id,
            user_id=user_id,
            role=VenueMemberRole.MEMBER,
        )
        db.add(member)

        # Increment members_count
        venue = await self.get_by_id(db, venue_id)
        if venue:
            venue.members_count += 1

        await db.flush()
        return True

    async def leave(self, db: AsyncSession, venue_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Leave a venue (only non-owners can leave)"""
        result = await db.execute(
            select(VenueMember).where(
                and_(
                    VenueMember.venue_id == venue_id,
                    VenueMember.user_id == user_id,
                )
            )
        )
        member = result.scalar_one_or_none()
        if not member or member.role == VenueMemberRole.OWNER:
            return False  # Not member or is owner (can't leave)

        await db.delete(member)

        # Decrement members_count
        venue = await self.get_by_id(db, venue_id)
        if venue and venue.members_count > 0:
            venue.members_count -= 1

        await db.flush()
        return True

    async def is_member(self, db: AsyncSession, venue_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is member of venue"""
        result = await db.execute(
            select(VenueMember).where(
                and_(
                    VenueMember.venue_id == venue_id,
                    VenueMember.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_member_role(self, db: AsyncSession, venue_id: uuid.UUID, user_id: uuid.UUID) -> Optional[str]:
        """Get user's role in venue"""
        result = await db.execute(
            select(VenueMember).where(
                and_(
                    VenueMember.venue_id == venue_id,
                    VenueMember.user_id == user_id,
                )
            )
        )
        member = result.scalar_one_or_none()
        return member.role if member else None

    async def get_venue_members(
        self,
        db: AsyncSession,
        venue_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[VenueMember], int]:
        """Get venue members list"""
        query = select(VenueMember).where(VenueMember.venue_id == venue_id)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginated results
        query = query.order_by(VenueMember.joined_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        members = result.scalars().all()

        return list(members), total

    async def get_venue_followers(
        self,
        db: AsyncSession,
        venue_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[VenueFollower], int]:
        """Get venue followers list"""
        query = select(VenueFollower).where(VenueFollower.venue_id == venue_id)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginated results
        query = query.order_by(VenueFollower.followed_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        followers = result.scalars().all()

        return list(followers), total


venue_service = VenueService()
