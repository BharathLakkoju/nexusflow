"""
SQLAlchemy ORM models for NexusFlow AI.
Implements: F-001–F-041 (all data persistence requirements).
"""
import uuid
from datetime import datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Organization & Auth
# ---------------------------------------------------------------------------

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    owner_id = Column(String(255), nullable=False, index=True)  # Stack Auth user ID
    plan = Column(String(50), default="free", nullable=False)
    monthly_token_limit = Column(Integer, default=1_000_000, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="organization", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(255), nullable=False)  # Stack Auth user ID
    user_email = Column(String(255))
    user_name = Column(String(255))
    role = Column(String(50), nullable=False, default="member")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('owner', 'admin', 'member', 'viewer')", name="ck_member_role"),
        UniqueConstraint("org_id", "user_id", name="uq_org_member"),
        Index("ix_org_members_user_id", "user_id"),
    )

    organization = relationship("Organization", back_populates="members")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    key_prefix = Column(String(20), nullable=False)  # First 8 chars for display
    permissions = Column(JSONB, default=["read", "write"])
    last_used_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="api_keys")


# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    nodes = Column(JSONB, nullable=False, default=list)
    edges = Column(JSONB, nullable=False, default=list)
    version = Column(Integer, default=1, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="draft", nullable=False)
    trigger_type = Column(String(50), default="manual", nullable=False)
    trigger_config = Column(JSONB, default=dict)
    webhook_id = Column(String(100), unique=True)  # for webhook trigger
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'active', 'archived')", name="ck_workflow_status"),
        CheckConstraint(
            "trigger_type IN ('manual', 'webhook', 'schedule', 'api')",
            name="ck_workflow_trigger"
        ),
    )

    organization = relationship("Organization", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    versions = relationship("WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowVersion(Base):
    __tablename__ = "workflow_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    nodes = Column(JSONB, nullable=False)
    edges = Column(JSONB, nullable=False)
    change_summary = Column(Text)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("workflow_id", "version", name="uq_workflow_version"),)

    workflow = relationship("Workflow", back_populates="versions")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False)
    input = Column(JSONB, default=dict)
    output = Column(JSONB)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Numeric(12, 8), default=0)
    triggered_by = Column(String(255))
    inngest_run_id = Column(String(255))  # Track Inngest job ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'waiting_approval')",
            name="ck_execution_status",
        ),
    )

    workflow = relationship("Workflow", back_populates="executions")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")
    agent_executions = relationship("AgentExecution", back_populates="execution", cascade="all, delete-orphan")
    approvals = relationship("HumanApproval", back_populates="execution", cascade="all, delete-orphan")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False
    )
    node_id = Column(String(255))
    agent_type = Column(String(50))
    level = Column(String(20), default="info", nullable=False)
    message = Column(Text, nullable=False)
    log_metadata = Column("metadata", JSONB, default=dict)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("level IN ('debug', 'info', 'warn', 'error')", name="ck_log_level"),
        Index("ix_execution_logs_exec_id", "execution_id"),
        Index("ix_execution_logs_ts", "timestamp"),
    )

    execution = relationship("WorkflowExecution", back_populates="logs")


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    system_prompt = Column(Text)
    model = Column(String(255), default="openai/gpt-4o-mini", nullable=False)
    temperature = Column(Numeric(3, 2), default=Decimal("0.70"))
    max_tokens = Column(Integer, default=2000)
    tools = Column(JSONB, default=list)  # list of tool names/IDs
    config = Column(JSONB, default=dict)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('research', 'planner', 'executor', 'critic', 'memory', 'supervisor', 'custom')",
            name="ck_agent_type",
        ),
    )

    organization = relationship("Organization", back_populates="agents")
    executions = relationship("AgentExecution", back_populates="agent")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    agent_type = Column(String(50), nullable=False)
    node_id = Column(String(255))
    status = Column(String(50), default="pending", nullable=False)
    input = Column(JSONB, default=dict)
    output = Column(JSONB)
    reasoning = Column(Text)
    tokens_used = Column(Integer, default=0)
    duration_ms = Column(Integer)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    execution = relationship("WorkflowExecution", back_populates="agent_executions")
    agent = relationship("Agent", back_populates="executions")


# ---------------------------------------------------------------------------
# Documents & RAG
# ---------------------------------------------------------------------------

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_url = Column(Text)  # Vercel Blob URL
    file_size = Column(Integer)
    status = Column(String(50), default="pending", nullable=False)
    chunk_count = Column(Integer, default=0)
    error_message = Column(Text)
    doc_metadata = Column(JSONB, default=dict)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_document_status",
        ),
    )

    organization = relationship("Organization", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(1536))
    chunk_metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="SET NULL"), nullable=True)
    memory_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    relevance_score = Column(Numeric(5, 4))
    mem_metadata = Column(JSONB, default=dict)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "memory_type IN ('short_term', 'long_term', 'episodic', 'semantic')",
            name="ck_memory_type",
        ),
        Index("ix_memories_org_type", "org_id", "memory_type"),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    config = Column(JSONB, default=dict)
    is_builtin = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "type IN ('web_search', 'http', 'code_exec', 'file', 'email', 'slack', 'custom')",
            name="ck_tool_type",
        ),
    )


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)
    workflow_id = Column(UUID(as_uuid=True))
    execution_id = Column(UUID(as_uuid=True))
    agent_type = Column(String(50))
    model = Column(String(255))
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost_estimate = Column(Numeric(12, 8), default=0)
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True, nullable=False)
    event_metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_analytics_org_id", "org_id"),
        Index("ix_analytics_created_at", "created_at"),
        Index("ix_analytics_event_type", "event_type"),
    )


# ---------------------------------------------------------------------------
# Human Approval (Human-in-the-loop)
# ---------------------------------------------------------------------------

class HumanApproval(Base):
    __tablename__ = "human_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False
    )
    node_id = Column(String(255), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    request_data = Column(JSONB, default=dict)
    response_data = Column(JSONB)
    approved_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_approval_status",
        ),
        Index("ix_approvals_execution_id", "execution_id"),
    )

    execution = relationship("WorkflowExecution", back_populates="approvals")
