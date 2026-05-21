"""
Pydantic schemas for all API request/response models.
Implements: all F-### data validation requirements.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Auth / User
# ---------------------------------------------------------------------------

class UserInfo(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    org_id: Optional[str] = None
    role: Optional[str] = None


class AuthSyncRequest(BaseModel):
    """Called after Stack Auth login to sync user to our DB."""
    org_name: Optional[str] = None  # For new users creating their first org


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

class OrgCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, max_length=100)


class OrgResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    owner_id: str
    plan: str
    monthly_token_limit: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberInvite(BaseModel):
    email: EmailStr
    role: str = Field(default="member", pattern="^(admin|member|viewer)$")


class MemberResponse(BaseModel):
    id: uuid.UUID
    user_id: str
    user_email: Optional[str]
    user_name: Optional[str]
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|member|viewer)$")


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------

class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    permissions: list[str] = Field(default=["read", "write"])
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    name: str
    key_prefix: str
    permissions: list[str]
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreateResponse(ApiKeyResponse):
    key: str  # Only returned once at creation


# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------

class WorkflowNodeData(BaseModel):
    label: str
    description: Optional[str] = None
    # Agent node
    agent_type: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    # Tool node
    tool_name: Optional[str] = None
    tool_config: Optional[dict] = None
    # Condition node
    condition_expression: Optional[str] = None
    # Loop node
    max_iterations: Optional[int] = None
    loop_condition: Optional[str] = None
    # Webhook node
    webhook_url: Optional[str] = None
    http_method: Optional[str] = None
    # Scheduler node
    cron_expression: Optional[str] = None
    # Human approval
    approval_message: Optional[str] = None
    timeout_minutes: Optional[int] = None
    # RAG node
    collection_id: Optional[str] = None
    top_k: Optional[int] = None
    # Memory node
    memory_type: Optional[str] = None
    memory_action: Optional[str] = None
    # Generic
    extra: Optional[dict[str, Any]] = None


class WorkflowNode(BaseModel):
    id: str
    type: str  # agent|tool|memory|rag|conditional|loop|human_approval|webhook|scheduler|start|end
    position: dict[str, float]
    data: WorkflowNodeData


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None
    label: Optional[str] = None
    animated: Optional[bool] = False
    data: Optional[dict] = None


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)
    trigger_type: str = Field(default="manual", pattern="^(manual|webhook|schedule|api)$")
    trigger_config: Optional[dict] = None
    is_template: bool = False


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    nodes: Optional[list[WorkflowNode]] = None
    edges: Optional[list[WorkflowEdge]] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|archived)$")
    trigger_type: Optional[str] = Field(None, pattern="^(manual|webhook|schedule|api)$")
    trigger_config: Optional[dict] = None
    change_summary: Optional[str] = None


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    nodes: list
    edges: list
    version: int
    status: str
    trigger_type: str
    is_template: bool
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class WorkflowVersionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    version: int
    nodes: list
    edges: list
    change_summary: Optional[str]
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowExecuteRequest(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict)
    model_override: Optional[str] = None


class ExecutionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: Optional[uuid.UUID]
    status: str
    input: dict
    output: Optional[dict]
    error: Optional[str]
    total_tokens: int
    estimated_cost: Optional[Decimal]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ExecutionLogEntry(BaseModel):
    id: uuid.UUID
    node_id: Optional[str]
    agent_type: Optional[str]
    level: str
    message: str
    log_metadata: dict
    timestamp: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(research|planner|executor|critic|memory|supervisor|custom)$")
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: str = Field(default="openai/gpt-4o-mini")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=32000)
    tools: list[str] = Field(default_factory=list)
    config: Optional[dict] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=32000)
    tools: Optional[list[str]] = None
    config: Optional[dict] = None


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    description: Optional[str]
    system_prompt: Optional[str]
    model: str
    temperature: Optional[Decimal]
    max_tokens: int
    tools: list
    config: dict
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentRunRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=10000)
    context: Optional[dict] = None
    model_override: Optional[str] = None


class AgentRunResponse(BaseModel):
    execution_id: uuid.UUID
    agent_id: uuid.UUID
    status: str
    output: Optional[str] = None
    reasoning: Optional[str] = None
    tokens_used: int = 0


# ---------------------------------------------------------------------------
# Documents & RAG
# ---------------------------------------------------------------------------

class DocumentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    file_type: str = Field(..., min_length=1, max_length=50)
    file_url: str = Field(..., min_length=1, max_length=5000)
    file_size: Optional[int] = Field(default=None, ge=0)


class DocumentResponse(BaseModel):
    id: uuid.UUID
    name: str
    file_type: str
    file_url: Optional[str]
    file_size: Optional[int]
    status: str
    chunk_count: int
    error_message: Optional[str]
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    use_hybrid: bool = True
    min_score: float = Field(default=0.3, ge=0.0, le=1.0)
    document_ids: Optional[list[uuid.UUID]] = None


class RAGSearchResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    content: str
    similarity: float
    chunk_index: int
    metadata: dict


class RAGSearchResponse(BaseModel):
    query: str
    results: list[RAGSearchResult]
    total: int


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    memory_type: str = Field(
        default="long_term",
        pattern="^(short_term|long_term|episodic|semantic)$"
    )
    agent_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    expires_in_hours: Optional[int] = Field(None, ge=1, le=8760)
    metadata: Optional[dict] = None


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    memory_type: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    agent_id: Optional[uuid.UUID] = None


class MemorySearchResponse(BaseModel):
    results: list[MemoryResponse]
    total: int


class MemoryResponse(BaseModel):
    id: uuid.UUID
    memory_type: str
    content: str
    relevance_score: Optional[Decimal]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(web_search|http|code_exec|file|email|slack|custom)$")
    description: Optional[str] = None
    config: Optional[dict] = None


class ToolResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    description: Optional[str]
    config: dict
    is_builtin: bool

    model_config = {"from_attributes": True}


class ToolExecuteRequest(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict)
    org_id: Optional[str] = None


class ToolExecuteResponse(BaseModel):
    tool_name: str
    output: Any
    success: bool
    error: Optional[str] = None
    latency_ms: int


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class AnalyticsDashboard(BaseModel):
    total_executions: int
    successful_executions: int
    failed_executions: int
    active_workflows: int
    total_tokens: int
    total_cost: Decimal
    avg_latency_ms: Optional[float]
    executions_by_day: list[dict]
    token_usage_by_model: list[dict]
    top_workflows: list[dict]
    agent_performance: list[dict]
    cost_by_day: list[dict]


# ---------------------------------------------------------------------------
# Human Approvals
# ---------------------------------------------------------------------------

class ApprovalResponse(BaseModel):
    id: uuid.UUID
    execution_id: uuid.UUID
    node_id: str
    status: str
    request_data: dict
    response_data: Optional[dict]
    approved_by: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ApprovalAction(BaseModel):
    action: str = Field(..., pattern="^(approved|rejected)$")
    response_data: Optional[dict] = None
    comment: Optional[str] = None


# ---------------------------------------------------------------------------
# Prompt Studio
# ---------------------------------------------------------------------------

class PromptRunRequest(BaseModel):
    system_prompt: str = Field(..., max_length=10000)
    user_message: str = Field(..., min_length=1, max_length=10000)
    model: str = Field(default="openai/gpt-4o-mini")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=32000)
    stream: bool = True


class PromptRunResponse(BaseModel):
    content: str
    model: str
    tokens_input: int
    tokens_output: int
    cost_estimate: Decimal
    latency_ms: int


# ---------------------------------------------------------------------------
# SSE Events
# ---------------------------------------------------------------------------

class SSEEvent(BaseModel):
    type: str  # log|node_start|node_complete|node_error|execution_complete|execution_failed|approval_required
    execution_id: str
    timestamp: str
    data: dict[str, Any]
