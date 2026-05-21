"""
RBAC (Role-Based Access Control) dependency factories.
Usage:
    @router.delete("/workflows/{id}")
    async def delete(user: UserInfo = Depends(require_role("admin"))):
        ...
"""
from functools import lru_cache
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.schemas.schemas import UserInfo

# Role hierarchy: higher index = more permissions
ROLE_HIERARCHY = ["viewer", "member", "admin", "owner"]


def _role_index(role: str) -> int:
    try:
        return ROLE_HIERARCHY.index(role)
    except ValueError:
        return -1


def require_role(minimum_role: str) -> Callable:
    """
    Dependency factory that ensures the current user has at least `minimum_role`.
    """
    async def dependency(user: UserInfo = Depends(get_current_user)) -> UserInfo:
        if not user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No organization membership found",
            )
        if _role_index(user.role) < _role_index(minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires '{minimum_role}' role or higher. Current role: '{user.role}'",
            )
        return user

    return dependency


def require_org(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    """Ensures user belongs to an organization."""
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must belong to an organization to perform this action.",
        )
    return user


# Convenience aliases
RequireViewer = Depends(require_role("viewer"))
RequireMember = Depends(require_role("member"))
RequireAdmin = Depends(require_role("admin"))
RequireOwner = Depends(require_role("owner"))
