"""
Organization service - team management
"""
import secrets
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql.organization import Organization, OrganizationInvite, InviteStatus, OrganizationPlan
from app.models.sql.user import User


class OrganizationService:
    """Service for organization/team management"""

    def _slugify(self, name: str) -> str:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        return slug

    async def create(self, db: AsyncSession, name: str, owner_id: uuid.UUID) -> Organization:
        slug = self._slugify(name)

        # Ensure unique slug
        result = await db.execute(select(Organization).where(Organization.slug == slug))
        existing = result.scalar_one_or_none()
        if existing:
            slug = f"{slug}-{secrets.token_hex(3)}"

        org = Organization(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            owner_id=owner_id,
            plan=OrganizationPlan.GRAND_SLAM,
            max_members=10,
            members=[{
                "user_id": str(owner_id),
                "role": "owner",
                "joined_at": datetime.utcnow().isoformat()
            }],
        )
        db.add(org)
        await db.flush()

        # Update user with org info
        user_result = await db.execute(select(User).where(User.id == owner_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.organization_id = org.id
            user.organization_role = "owner"
            await db.flush()

        await db.refresh(org)
        return org

    async def get_by_id(self, db: AsyncSession, org_id: uuid.UUID) -> Optional[Organization]:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalar_one_or_none()

    async def get_by_owner(self, db: AsyncSession, owner_id: uuid.UUID) -> Optional[Organization]:
        result = await db.execute(select(Organization).where(Organization.owner_id == owner_id))
        return result.scalar_one_or_none()

    async def get_user_org(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[Organization]:
        # Query user to get organization_id
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user or not user.organization_id:
            return None

        return await self.get_by_id(db, user.organization_id)

    async def create_invite(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        email: str,
        role: str,
        invited_by: uuid.UUID
    ) -> OrganizationInvite:
        token = secrets.token_urlsafe(32)
        invite = OrganizationInvite(
            id=uuid.uuid4(),
            organization_id=org_id,
            email=email,
            role=role,
            token=token,
            invited_by=invited_by,
            status=InviteStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(invite)
        await db.flush()
        await db.refresh(invite)
        return invite

    async def accept_invite(self, db: AsyncSession, token: str, user_id: uuid.UUID) -> bool:
        result = await db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.token == token,
                OrganizationInvite.status == InviteStatus.PENDING,
                OrganizationInvite.expires_at > datetime.utcnow()
            )
        )
        invite = result.scalar_one_or_none()
        if not invite:
            return False

        # Check max members
        org = await self.get_by_id(db, invite.organization_id)
        if not org:
            return False

        if len(org.members or []) >= org.max_members:
            return False

        # Add member to org
        members = org.members or []
        members.append({
            "user_id": str(user_id),
            "role": invite.role,
            "joined_at": datetime.utcnow().isoformat()
        })
        org.members = members

        # Update user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.organization_id = org.id
            user.organization_role = invite.role

        # Mark invite as accepted
        invite.status = InviteStatus.ACCEPTED

        await db.flush()
        return True

    async def remove_member(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        requester_id: uuid.UUID
    ) -> bool:
        org = await self.get_by_id(db, org_id)
        if not org:
            return False

        # Only owner or admin can remove members
        requester_member = next(
            (m for m in (org.members or []) if m.get("user_id") == str(requester_id)),
            None
        )
        if not requester_member or requester_member.get("role") not in ("owner", "admin"):
            return False

        # Can't remove owner
        if org.owner_id == user_id:
            return False

        # Remove member from org
        org.members = [m for m in (org.members or []) if m.get("user_id") != str(user_id)]

        # Update user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.organization_id = None
            user.organization_role = None

        await db.flush()
        return True

    async def get_org_invites(self, db: AsyncSession, org_id: uuid.UUID) -> list[OrganizationInvite]:
        result = await db.execute(
            select(OrganizationInvite)
            .where(
                OrganizationInvite.organization_id == org_id,
                OrganizationInvite.status == InviteStatus.PENDING
            )
            .order_by(OrganizationInvite.created_at.desc())
            .limit(100)
        )
        return list(result.scalars().all())


organization_service = OrganizationService()
