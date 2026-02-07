"""
Organizations API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.dependencies import require_grand_slam
from app.models.user import UserInDB
from app.models.organization import OrganizationCreate, InviteCreate
from app.services.organization_service import organization_service
from app.services.email_service import email_service

router = APIRouter(tags=["organizations"])


@router.post("/")
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(require_grand_slam),
):
    """Create a new organization (Grand Slam only)"""
    # Check if user already has an org
    existing = await organization_service.get_user_org(db, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Voce ja pertence a uma organizacao")

    org = await organization_service.create(db, data.name, current_user.id)
    # Convert to dict for response
    return {
        "_id": str(org.id),
        "name": org.name,
        "slug": org.slug,
        "ownerId": str(org.owner_id),
        "plan": org.plan,
        "maxMembers": org.max_members,
        "members": org.members,
        "createdAt": org.created_at,
        "updatedAt": org.updated_at,
    }


@router.get("/me")
async def get_my_organization(
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Get current user's organization"""
    org = await organization_service.get_user_org(db, current_user.id)
    if not org:
        return None
    return {
        "_id": str(org.id),
        "name": org.name,
        "slug": org.slug,
        "ownerId": str(org.owner_id),
        "plan": org.plan,
        "maxMembers": org.max_members,
        "members": org.members,
        "createdAt": org.created_at,
        "updatedAt": org.updated_at,
    }


@router.post("/invite")
async def invite_member(
    data: InviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Invite a member to the organization"""
    org = await organization_service.get_user_org(db, current_user.id)
    if not org:
        raise HTTPException(status_code=404, detail="Voce nao pertence a nenhuma organizacao")

    # Check if user is owner or admin
    user_member = next(
        (m for m in (org.members or []) if m.get("user_id") == str(current_user.id)),
        None
    )
    if not user_member or user_member.get("role") not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Sem permissao para convidar membros")

    # Check max members
    if len(org.members or []) >= org.max_members:
        raise HTTPException(status_code=400, detail="Limite de membros atingido")

    invite = await organization_service.create_invite(
        db=db,
        org_id=org.id,
        email=data.email,
        role=data.role,
        invited_by=current_user.id,
    )

    # Send invite email
    await email_service.send_organization_invite(
        to=data.email,
        org_name=org.name,
        inviter_name=current_user.fullName,
        token=invite.token,
    )

    return {"message": "Convite enviado com sucesso"}


@router.post("/accept-invite")
async def accept_invite(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Accept an organization invite"""
    success = await organization_service.accept_invite(db, token, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Convite invalido, expirado ou organizacao cheia")
    return {"message": "Convite aceito com sucesso"}


@router.delete("/members/{user_id}")
async def remove_member(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Remove a member from the organization"""
    import uuid as uuid_module

    org = await organization_service.get_user_org(db, current_user.id)
    if not org:
        raise HTTPException(status_code=404, detail="Voce nao pertence a nenhuma organizacao")

    try:
        user_uuid = uuid_module.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario invalido")

    success = await organization_service.remove_member(
        db=db,
        org_id=org.id,
        user_id=user_uuid,
        requester_id=current_user.id,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Nao foi possivel remover o membro")

    return {"message": "Membro removido com sucesso"}


@router.get("/invites")
async def get_invites(
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Get pending invites for current user's organization"""
    org = await organization_service.get_user_org(db, current_user.id)
    if not org:
        return []
    invites = await organization_service.get_org_invites(db, org.id)
    return [
        {
            "_id": str(invite.id),
            "organizationId": str(invite.organization_id),
            "email": invite.email,
            "role": invite.role,
            "token": invite.token,
            "invitedBy": str(invite.invited_by),
            "status": invite.status,
            "expiresAt": invite.expires_at,
            "createdAt": invite.created_at,
        }
        for invite in invites
    ]
