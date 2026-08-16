"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension (Neon supports this on all plans)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Organizations
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("owner_id", sa.String(255), nullable=False),
        sa.Column("plan", sa.String(50), nullable=False, server_default="free"),
        sa.Column("monthly_token_limit", sa.Integer(), nullable=False, server_default="1000000"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_index("ix_organizations_owner_id", "organizations", ["owner_id"])

    # Organization Members
    op.create_table(
        "organization_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("user_email", sa.String(255)),
        sa.Column("user_name", sa.String(255)),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('owner', 'admin', 'member', 'viewer')", name="ck_member_role"),
        sa.UniqueConstraint("org_id", "user_id", name="uq_org_member"),
    )
    op.create_index("ix_org_members_user_id", "organization_members", ["user_id"])

    # API Keys
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("key_prefix", sa.String(20), nullable=False),
        sa.Column("permissions", postgresql.JSONB(), server_default='["read","write"]'),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("key_hash", name="uq_api_key_hash"),
    )

    # Workflows
    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("nodes", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("edges", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_template", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("trigger_type", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("trigger_config", postgresql.JSONB(), server_default="{}"),
        sa.Column("webhook_id", sa.String(100)),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('draft', 'active', 'archived')", name="ck_workflow_status"),
        sa.CheckConstraint("trigger_type IN ('manual', 'webhook', 'schedule', 'api')", name="ck_workflow_trigger"),
        sa.UniqueConstraint("webhook_id", name="uq_workflow_webhook_id"),
    )
    op.create_index("ix_workflows_org_id", "workflows", ["org_id"])

    # Workflow Versions
    op.create_table(
        "workflow_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("nodes", postgresql.JSONB(), nullable=False),
        sa.Column("edges", postgresql.JSONB(), nullable=False),
        sa.Column("change_summary", sa.Text()),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("workflow_id", "version", name="uq_workflow_version"),
    )
    op.create_index("ix_workflow_versions_wf_id", "workflow_versions", ["workflow_id"])

    # Workflow Executions
    op.create_table(
        "workflow_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("input", postgresql.JSONB(), server_default="{}"),
        sa.Column("output", postgresql.JSONB()),
        sa.Column("error", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("total_tokens", sa.Integer(), server_default="0"),
        sa.Column("estimated_cost", sa.Numeric(12, 8), server_default="0"),
        sa.Column("triggered_by", sa.String(255)),
        sa.Column("inngest_run_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('pending','running','completed','failed','cancelled','waiting_approval')",
            name="ck_execution_status",
        ),
    )
    op.create_index("ix_workflow_executions_org_id", "workflow_executions", ["org_id"])
    op.create_index("ix_workflow_executions_created_at", "workflow_executions", ["created_at"])

    # Execution Logs
    op.create_table(
        "execution_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_id", sa.String(255)),
        sa.Column("agent_type", sa.String(50)),
        sa.Column("level", sa.String(20), nullable=False, server_default="info"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("level IN ('debug','info','warn','error')", name="ck_log_level"),
    )
    op.create_index("ix_execution_logs_exec_id", "execution_logs", ["execution_id"])
    op.create_index("ix_execution_logs_ts", "execution_logs", ["timestamp"])

    # Agents
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("system_prompt", sa.Text()),
        sa.Column("model", sa.String(255), nullable=False, server_default="openai/gpt-4o-mini"),
        sa.Column("temperature", sa.Numeric(3, 2), server_default="0.70"),
        sa.Column("max_tokens", sa.Integer(), server_default="2000"),
        sa.Column("tools", postgresql.JSONB(), server_default="[]"),
        sa.Column("config", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "type IN ('research','planner','executor','critic','memory','supervisor','custom')",
            name="ck_agent_type",
        ),
    )
    op.create_index("ix_agents_org_id", "agents", ["org_id"])

    # Agent Executions
    op.create_table(
        "agent_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_type", sa.String(50), nullable=False),
        sa.Column("node_id", sa.String(255)),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("input", postgresql.JSONB(), server_default="{}"),
        sa.Column("output", postgresql.JSONB()),
        sa.Column("reasoning", sa.Text()),
        sa.Column("tokens_used", sa.Integer(), server_default="0"),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_agent_executions_exec_id", "agent_executions", ["execution_id"])

    # Documents
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("file_url", sa.Text()),
        sa.Column("file_size", sa.Integer()),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("chunk_count", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("doc_metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('pending','processing','completed','failed')", name="ck_document_status"
        ),
    )
    op.create_index("ix_documents_org_id", "documents", ["org_id"])

    # Document Chunks (with vector embedding)
    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Add vector column and HNSW index via raw SQL (pgvector-specific)
    op.execute("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding vector(1536)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_doc_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops)")
    op.create_index("ix_doc_chunks_doc_id", "document_chunks", ["document_id"])
    op.create_index("ix_doc_chunks_org_id", "document_chunks", ["org_id"])

    # Memories
    op.create_table(
        "memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_executions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("memory_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("relevance_score", sa.Numeric(5, 4)),
        sa.Column("mem_metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "memory_type IN ('short_term','long_term','episodic','semantic')", name="ck_memory_type"
        ),
    )
    op.execute("ALTER TABLE memories ADD COLUMN IF NOT EXISTS embedding vector(1536)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_memories_embedding ON memories USING hnsw (embedding vector_cosine_ops)")
    op.create_index("ix_memories_org_type", "memories", ["org_id", "memory_type"])

    # Tools
    op.create_table(
        "tools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("config", postgresql.JSONB(), server_default="{}"),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "type IN ('web_search','http','code_exec','file','email','slack','custom')",
            name="ck_tool_type",
        ),
    )

    # Analytics Events
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True)),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True)),
        sa.Column("agent_type", sa.String(50)),
        sa.Column("model", sa.String(255)),
        sa.Column("tokens_input", sa.Integer(), server_default="0"),
        sa.Column("tokens_output", sa.Integer(), server_default="0"),
        sa.Column("cost_estimate", sa.Numeric(12, 8), server_default="0"),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("event_metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_analytics_org_id", "analytics_events", ["org_id"])
    op.create_index("ix_analytics_created_at", "analytics_events", ["created_at"])

    # Human Approvals
    op.create_table(
        "human_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("request_data", postgresql.JSONB(), server_default="{}"),
        sa.Column("response_data", postgresql.JSONB()),
        sa.Column("approved_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_approval_status"
        ),
    )
    op.create_index("ix_approvals_execution_id", "human_approvals", ["execution_id"])


def downgrade() -> None:
    op.drop_table("human_approvals")
    op.drop_table("analytics_events")
    op.drop_table("tools")
    op.drop_table("memories")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("agent_executions")
    op.drop_table("agents")
    op.drop_table("execution_logs")
    op.drop_table("workflow_executions")
    op.drop_table("workflow_versions")
    op.drop_table("workflows")
    op.drop_table("api_keys")
    op.drop_table("organization_members")
    op.drop_table("organizations")
    op.execute("DROP EXTENSION IF EXISTS vector")
