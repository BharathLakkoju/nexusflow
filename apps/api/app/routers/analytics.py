# Implements: F-040 (analytics dashboard)
"""Analytics router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireViewer
from app.schemas.schemas import AnalyticsDashboard
from app.services.analytics_service import get_dashboard

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    days: int = Query(default=30, ge=1, le=90),
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsDashboard:
    """Get analytics dashboard for the organization."""
    return await get_dashboard(db, str(current_user.org_id), days=days)
