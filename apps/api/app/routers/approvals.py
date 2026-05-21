# Implements: F-041 (human-in-the-loop approvals)
"""Human approval router."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember, RequireViewer
from app.models.models import HumanApproval
from app.schemas.schemas import ApprovalAction, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalResponse])
async def list_pending_approvals(
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[ApprovalResponse]:
    result = await db.execute(
        select(HumanApproval)
        .where(
            HumanApproval.org_id == current_user.org_id,
            HumanApproval.status == "pending",
        )
        .order_by(HumanApproval.created_at.desc())
    )
    approvals = result.scalars().all()
    return [ApprovalResponse.model_validate(a) for a in approvals]


@router.post("/{approval_id}/action", response_model=ApprovalResponse)
async def action_approval(
    approval_id: UUID,
    body: ApprovalAction,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    result = await db.execute(
        select(HumanApproval).where(
            HumanApproval.id == approval_id,
            HumanApproval.org_id == current_user.org_id,
        )
    )
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail=f"Approval is already '{approval.status}'")

    approval.status = body.action  # "approved" or "rejected"
    approval.responded_by = current_user.user_id
    approval.response_comment = body.comment
    await db.commit()
    await db.refresh(approval)
    return ApprovalResponse.model_validate(approval)
