# Implements: F-025 (document management)
"""
Documents router: upload metadata + trigger ingestion.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember, RequireViewer
from app.models.models import Document
from app.schemas.schemas import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    body: DocumentCreate,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """
    Register a document that was already uploaded to Vercel Blob.
    Triggers async ingestion via Inngest.
    """
    doc = Document(
        org_id=current_user.org_id,
        name=body.name,
        file_url=body.file_url,
        file_type=body.file_type,
        file_size=body.file_size,
        status="pending",
        created_by=current_user.user_id,
    )
    db.add(doc)
    await db.flush()
    doc_id = str(doc.id)
    await db.commit()

    # Trigger Inngest ingestion job
    from app.inngest.client import inngest_client
    import inngest

    await inngest_client.send(
        inngest.Event(
            name="nexusflow/document.ingest",
            data={"document_id": doc_id},
        )
    )

    await db.refresh(doc)
    return DocumentResponse.model_validate(doc)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    result = await db.execute(
        select(Document)
        .where(Document.org_id == current_user.org_id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.org_id == current_user.org_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.org_id == current_user.org_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()
