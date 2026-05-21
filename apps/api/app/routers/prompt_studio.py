# Implements: F-039 (prompt studio)
"""
Prompt Studio router: test prompts against LLMs with optional RAG context.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember
from app.schemas.schemas import PromptRunRequest, PromptRunResponse

router = APIRouter(prefix="/prompt-studio", tags=["prompt-studio"])


@router.post("/run", response_model=PromptRunResponse)
async def run_prompt(
    body: PromptRunRequest,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> PromptRunResponse:
    """Run a prompt against an LLM with optional RAG context injection."""
    import time

    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    from app.config import settings
    from app.services.rag_service import build_rag_context

    start = time.time()
    model = body.model or settings.DEFAULT_MODEL
    org_id = str(current_user.org_id)

    # Optionally inject RAG context
    rag_context = ""
    if body.use_rag and body.rag_query:
        rag_context = await build_rag_context(db, org_id, body.rag_query, top_k=5)

    llm = ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=body.temperature or 0.7,
        max_tokens=body.max_tokens or 2048,
        default_headers={
            "HTTP-Referer": settings.FRONTEND_URL,
            "X-Title": "NexusFlow AI Prompt Studio",
        },
    )

    messages = []
    system_prompt = body.system_prompt or "You are a helpful AI assistant."
    if rag_context:
        system_prompt += f"\n\n{rag_context}"
    messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=body.user_prompt))

    response = await llm.ainvoke(messages)
    latency_ms = int((time.time() - start) * 1000)

    # Extract token usage if available
    usage = {}
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage = {
            "input_tokens": response.usage_metadata.get("input_tokens", 0),
            "output_tokens": response.usage_metadata.get("output_tokens", 0),
        }

    return PromptRunResponse(
        output=response.content,
        model=model,
        latency_ms=latency_ms,
        rag_context_used=bool(rag_context),
        usage=usage,
    )
