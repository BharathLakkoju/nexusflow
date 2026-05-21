# Implements: F-004 (API keys)
"""
API Keys router: create and manage API keys for org programmatic access.
"""
import hashlib
import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireAdmin, RequireViewer
from app.models.models import ApiKey
from app.schemas.schemas import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyResponse,
)

router = APIRouter(prefix="/organizations/{org_id}/keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    org_id: UUID,
    body: ApiKeyCreateRequest,
    current_user: UserInfo = Depends(RequireAdmin),
    db: AsyncSession = Depends(get_db),
) -> ApiKeyCreateResponse:
    """Create a new API key. The plaintext key is returned ONCE — store it safely."""
    # Generate secure random key: nf_<48 hex chars>
    raw_key = "nf_" + secrets.token_hex(24)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:10]

    api_key = ApiKey(
        org_id=org_id,
        name=body.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        created_by=current_user.user_id,
        scopes=body.scopes or ["*"],
        expires_at=body.expires_at,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key=raw_key,  # Only returned once
        key_prefix=key_prefix,
        scopes=api_key.scopes,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
    )


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    org_id: UUID,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[ApiKeyResponse]:
    result = await db.execute(
        select(ApiKey).where(ApiKey.org_id == org_id, ApiKey.is_active == True)
    )
    keys = result.scalars().all()
    return [ApiKeyResponse.model_validate(k) for k in keys]


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    org_id: UUID,
    key_id: UUID,
    current_user: UserInfo = Depends(RequireAdmin),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.org_id == org_id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    await db.commit()
