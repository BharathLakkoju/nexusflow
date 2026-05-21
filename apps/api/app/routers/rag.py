# Implements: F-026 (RAG search)
"""RAG search router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireViewer
from app.schemas.schemas import RAGSearchRequest, RAGSearchResponse
from app.services.rag_service import search_documents

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/search", response_model=RAGSearchResponse)
async def rag_search(
    body: RAGSearchRequest,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> RAGSearchResponse:
    """Semantic search over documents in the organization."""
    return await search_documents(db, str(current_user.org_id), body)
