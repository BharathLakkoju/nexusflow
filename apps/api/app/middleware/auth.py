"""
Authentication middleware: verifies Stack Auth (Neon Auth) JWTs
and optionally API key authentication.
"""
import hashlib
import logging
import time
from typing import Optional

import httpx
import jwt
from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient, PyJWKClientError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.models.models import ApiKey, Organization, OrganizationMember
from app.schemas.schemas import UserInfo

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stack Auth JWT verification
# ---------------------------------------------------------------------------

_jwks_client: Optional[PyJWKClient] = None
_jwks_last_refresh: float = 0
_JWKS_CACHE_TTL = 3600  # 1 hour


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client, _jwks_last_refresh
    now = time.time()
    if _jwks_client is None or (now - _jwks_last_refresh) > _JWKS_CACHE_TTL:
        _jwks_client = PyJWKClient(
            settings.NEON_AUTH_JWKS_URL,
            cache_jwk_set=True,
            lifespan=_JWKS_CACHE_TTL,
        )
        _jwks_last_refresh = now
    return _jwks_client


def verify_stack_token(token: str) -> dict:
    """Verify a Stack Auth access token and return its payload."""
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256", "ES256"],
            options={"verify_aud": False},  # Stack Auth sub-claim is sufficient
        )
        return payload
    except PyJWKClientError as exc:
        logger.warning("JWKS error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to verify token signature",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.DecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        )


# ---------------------------------------------------------------------------
# FastAPI security schemes
# ---------------------------------------------------------------------------

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    x_api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> UserInfo:
    """
    FastAPI dependency. Accepts either:
    - Bearer <Stack Auth JWT>
    - X-API-Key <nexusflow API key>
    """
    # --- Bearer token (Stack Auth JWT) ---
    if credentials and credentials.credentials:
        token = credentials.credentials
        payload = verify_stack_token(token)
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub claim")

        # Look up org membership
        result = await db.execute(
            select(OrganizationMember, Organization)
            .join(Organization, OrganizationMember.org_id == Organization.id)
            .where(OrganizationMember.user_id == user_id)
            .limit(1)
        )
        row = result.first()

        return UserInfo(
            user_id=user_id,
            email=payload.get("email"),
            name=payload.get("name"),
            org_id=str(row.Organization.id) if row else None,
            role=row.OrganizationMember.role if row else None,
        )

    # --- API Key ---
    if x_api_key:
        # Hash the presented key and look up in DB
        key_hash = _hash_api_key(x_api_key)
        result = await db.execute(
            select(ApiKey, Organization)
            .join(Organization, ApiKey.org_id == Organization.id)
            .where(ApiKey.key_hash == key_hash)
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

        api_key_obj: ApiKey = row.ApiKey
        org: Organization = row.Organization

        # Check expiry
        if api_key_obj.expires_at and api_key_obj.expires_at < time.time():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key expired")

        # Update last_used_at asynchronously (fire and forget pattern via background)
        from datetime import datetime, timezone
        api_key_obj.last_used_at = datetime.now(timezone.utc)
        await db.commit()

        return UserInfo(
            user_id=f"apikey:{api_key_obj.id}",
            org_id=str(org.id),
            role="member",  # API keys default to member-level access
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide Bearer token or X-API-Key.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _hash_api_key(key: str) -> str:
    """SHA-256 hash of the API key for constant-time lookup."""
    return hashlib.sha256(key.encode()).hexdigest()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    x_api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserInfo]:
    """Like get_current_user but returns None instead of 401 for unauthenticated requests."""
    try:
        return await get_current_user(credentials, x_api_key, db)
    except HTTPException:
        return None
