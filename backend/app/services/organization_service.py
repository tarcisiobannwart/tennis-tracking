"""
Organization service - team management
"""
import secrets
import re
from datetime import datetime, timedelta
from typing import Optional
from app.core.mongodb import get_collection


class OrganizationService:
    """Service for organization/team management"""

    def __init__(self):
        self._orgs = None
        self._invites = None

    @property
    def orgs(self):
        if self._orgs is None:
            self._orgs = get_collection("organizations")
        return self._orgs

    @property
    def invites(self):
        if self._invites is None:
            self._invites = get_collection("organization_invites")
        return self._invites

    def _slugify(self, name: str) -> str:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        return slug

    async def create(self, name: str, owner_id: str) -> dict:
        slug = self._slugify(name)

        # Ensure unique slug
        existing = await self.orgs.find_one({"slug": slug})
        if existing:
            slug = f"{slug}-{secrets.token_hex(3)}"

        org = {
            "name": name,
            "slug": slug,
            "ownerId": owner_id,
            "plan": "grand_slam",
            "maxMembers": 10,
            "members": [{"userId": owner_id, "role": "owner", "joinedAt": datetime.utcnow()}],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }

        result = await self.orgs.insert_one(org)
        org["_id"] = str(result.inserted_id)

        # Update user with org info
        users = get_collection("users")
        await users.update_one(
            {"_id": owner_id},
            {"$set": {
                "organizationId": str(result.inserted_id),
                "organizationRole": "owner",
                "updatedAt": datetime.utcnow(),
            }}
        )

        return org

    async def get_by_id(self, org_id: str) -> Optional[dict]:
        org = await self.orgs.find_one({"_id": org_id})
        if org:
            org["_id"] = str(org["_id"])
        return org

    async def get_by_owner(self, owner_id: str) -> Optional[dict]:
        org = await self.orgs.find_one({"ownerId": owner_id})
        if org:
            org["_id"] = str(org["_id"])
        return org

    async def get_user_org(self, user_id: str) -> Optional[dict]:
        org = await self.orgs.find_one({"members.userId": user_id})
        if org:
            org["_id"] = str(org["_id"])
        return org

    async def create_invite(self, org_id: str, email: str, role: str, invited_by: str) -> dict:
        token = secrets.token_urlsafe(32)
        invite = {
            "organizationId": org_id,
            "email": email,
            "role": role,
            "token": token,
            "invitedBy": invited_by,
            "status": "pending",
            "expiresAt": datetime.utcnow() + timedelta(days=7),
            "createdAt": datetime.utcnow(),
        }
        await self.invites.insert_one(invite)
        return invite

    async def accept_invite(self, token: str, user_id: str) -> bool:
        invite = await self.invites.find_one({
            "token": token,
            "status": "pending",
            "expiresAt": {"$gt": datetime.utcnow()},
        })

        if not invite:
            return False

        org_id = invite["organizationId"]

        # Check max members
        org = await self.orgs.find_one({"_id": org_id})
        if not org:
            return False

        if len(org.get("members", [])) >= org.get("maxMembers", 10):
            return False

        # Add member to org
        await self.orgs.update_one(
            {"_id": org_id},
            {"$push": {"members": {
                "userId": user_id,
                "role": invite["role"],
                "joinedAt": datetime.utcnow(),
            }}}
        )

        # Update user
        users = get_collection("users")
        await users.update_one(
            {"_id": user_id},
            {"$set": {
                "organizationId": str(org_id) if not isinstance(org_id, str) else org_id,
                "organizationRole": invite["role"],
                "updatedAt": datetime.utcnow(),
            }}
        )

        # Mark invite as accepted
        await self.invites.update_one(
            {"token": token},
            {"$set": {"status": "accepted"}}
        )

        return True

    async def remove_member(self, org_id: str, user_id: str, requester_id: str) -> bool:
        org = await self.orgs.find_one({"_id": org_id})
        if not org:
            return False

        # Only owner or admin can remove members
        requester_member = next(
            (m for m in org.get("members", []) if m["userId"] == requester_id),
            None
        )
        if not requester_member or requester_member["role"] not in ("owner", "admin"):
            return False

        # Can't remove owner
        if org["ownerId"] == user_id:
            return False

        await self.orgs.update_one(
            {"_id": org_id},
            {"$pull": {"members": {"userId": user_id}}}
        )

        users = get_collection("users")
        await users.update_one(
            {"_id": user_id},
            {"$set": {
                "organizationId": None,
                "organizationRole": None,
                "updatedAt": datetime.utcnow(),
            }}
        )

        return True

    async def get_org_invites(self, org_id: str) -> list:
        invites = await self.invites.find(
            {"organizationId": org_id, "status": "pending"}
        ).sort("createdAt", -1).to_list(100)

        for invite in invites:
            invite["_id"] = str(invite["_id"])

        return invites


organization_service = OrganizationService()
