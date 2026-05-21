# Implements: F-002 (organizations), F-003 (RBAC)
"""
Organizations router: CRUD for orgs and member management.
"""
import secrets
import string
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo, get_current_user
from app.middleware.rbac import RequireAdmin, RequireOwner, RequireViewer
from app.models.models import Organization, OrganizationMember
from app.schemas.schemas import (
    MemberInviteRequest,
    MemberResponse,
    OrgCreate,
    OrgResponse,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: OrgCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgResponse:
    """Create a new organization. The creating user becomes the owner."""
    org = Organization(name=body.name, slug=_make_slug(body.name))
    db.add(org)
    await db.flush()

    member = OrganizationMember(
        org_id=org.id,
        user_id=current_user.user_id,
        email=current_user.email,
        role="owner",
    )
    db.add(member)
    await db.commit()
    await db.refresh(org)
    return OrgResponse.model_validate(org)


@router.get("/{org_id}", response_model=OrgResponse)
async def get_organization(
    org_id: UUID,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> OrgResponse:
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrgResponse.model_validate(org)


@router.get("/{org_id}/members", response_model=list[MemberResponse])
async def list_members(
    org_id: UUID,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[MemberResponse]:
    result = await db.execute(
        select(OrganizationMember).where(OrganizationMember.org_id == org_id)
    )
    members = result.scalars().all()
    return [MemberResponse.model_validate(m) for m in members]


@router.post("/{org_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: UUID,
    body: MemberInviteRequest,
    current_user: UserInfo = Depends(RequireAdmin),
    db: AsyncSession = Depends(get_db),
) -> MemberResponse:
    """Invite a user to the organization by email."""
    # Check not already a member
    existing = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.org_id == org_id,
            OrganizationMember.email == body.email,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User is already a member")

    member = OrganizationMember(
        org_id=org_id,
        user_id=None,  # Will be filled when user accepts invite
        email=body.email,
        role=body.role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return MemberResponse.model_validate(member)


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: UUID,
    user_id: str,
    current_user: UserInfo = Depends(RequireAdmin),
    db: AsyncSession = Depends(get_db),
) -> None:
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member.role == "owner":
        raise HTTPException(status_code=403, detail="Cannot remove the owner")
    await db.delete(member)
    await db.commit()


def _make_slug(name: str) -> str:
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{slug[:30]}-{suffix}"
