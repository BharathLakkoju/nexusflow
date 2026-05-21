# Implements: All F-### requirements — application entry point
"""
NexusFlow AI — FastAPI application entry point.
Assembles all routers, middleware, lifespan, health check, and Inngest endpoint.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import inngest.fast_api
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.db.database import engine
from app.inngest.client import inngest_client
from app.inngest.functions import INNGEST_FUNCTIONS
from app.routers import (
    agents,
    analytics,
    approvals,
    auth,
    documents,
    keys,
    memory,
    organizations,
    prompt_studio,
    rag,
    stream,
    tools,
    workflows,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter (slowapi wraps Redis for distributed limiting)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle."""
    logger.info("NexusFlow AI starting up...")
    # Test DB connection
    try:
        async with engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection OK")
    except Exception as exc:
        logger.error("Database connection FAILED: %s", exc)

    yield

    logger.info("NexusFlow AI shutting down...")
    await engine.dispose()


app = FastAPI(
    title="NexusFlow AI",
    description="AI Agent Workflow Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "https://nexusflow.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inngest endpoint ---
inngest.fast_api.serve(
    app,
    inngest_client,
    INNGEST_FUNCTIONS,
    serve_path="/inngest",
)

# --- API routers ---
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(organizations.router, prefix=API_PREFIX)
app.include_router(keys.router, prefix=API_PREFIX)
app.include_router(workflows.router, prefix=API_PREFIX)
app.include_router(agents.router, prefix=API_PREFIX)
app.include_router(documents.router, prefix=API_PREFIX)
app.include_router(rag.router, prefix=API_PREFIX)
app.include_router(memory.router, prefix=API_PREFIX)
app.include_router(tools.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
app.include_router(stream.router, prefix=API_PREFIX)
app.include_router(approvals.router, prefix=API_PREFIX)
app.include_router(prompt_studio.router, prefix=API_PREFIX)


# --- Health check ---
@app.get("/health", include_in_schema=False)
async def health() -> dict:
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"message": "NexusFlow AI API", "docs": "/docs"}


# --- Global exception handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s %s — %s", request.method, request.url, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )
