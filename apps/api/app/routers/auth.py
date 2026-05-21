# Implements: F-001 (auth)
"""
Auth router: user info endpoint (authentication is handled by Neon Auth / Stack Auth on frontend).
"""
from fastapi import APIRouter, Depends

from app.middleware.auth import UserInfo, get_current_user
from app.schemas.schemas import UserInfo as UserInfoSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserInfoSchema)
async def get_me(current_user: UserInfo = Depends(get_current_user)) -> UserInfoSchema:
    """Return the currently authenticated user's info."""
    return UserInfoSchema(
        user_id=current_user.user_id,
        email=current_user.email,
        org_id=current_user.org_id,
        role=current_user.role,
    )
