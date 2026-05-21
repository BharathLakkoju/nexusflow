/**
 * Demo seed data — shown as fallback when the API returns empty results.
 * This allows any new user or demo viewer to see a fully populated interface.
 */

import type {
  Workflow,
  Agent,
  Document,
  Memory,
  HumanApproval,
  AnalyticsDashboard,
} from "./api";

// ---------------------------------------------------------------------------
// Demo Workflows
// ---------------------------------------------------------------------------
export const DEMO_WORKFLOWS: Workflow[] = [
  {
    id: "demo-wf-001",
    name: "Customer Support Bot",
    description:
      "Automated customer support with human escalation for complex issues",
    status: "active",
    trigger_type: "manual",
    version: 3,
    created_at: new Date(Date.now() - 7 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    nodes: [
      {
        id: "start",
        type: "start",
        position: { x: 50, y: 200 },
        data: { label: "Start" },
      },
      {
        id: "agent-1",
        type: "agent",
        position: { x: 250, y: 200 },
        data: {
          label: "Support Agent",
          model: "meta-llama/llama-3.3-70b-instruct:free",
          system_prompt:
            "You are a helpful customer support agent. Resolve issues politely.",
        },
      },
      {
        id: "condition-1",
        type: "condition",
        position: { x: 450, y: 200 },
        data: { label: "Needs escalation?", condition: "confidence < 0.7" },
      },
      {
        id: "approval-1",
        type: "human_approval",
        position: { x: 650, y: 100 },
        data: { label: "Human Review", message: "Please review this customer case" },
      },
      {
        id: "end",
        type: "end",
        position: { x: 850, y: 200 },
        data: { label: "End" },
      },
    ],
    edges: [
      { id: "e1", source: "start", target: "agent-1" },
      { id: "e2", source: "agent-1", target: "condition-1" },
      { id: "e3", source: "condition-1", target: "approval-1", type: "true" },
      { id: "e4", source: "condition-1", target: "end", type: "false" },
      { id: "e5", source: "approval-1", target: "end" },
    ],
  },
  {
    id: "demo-wf-002",
    name: "Research & Summarize",
    description:
      "Search the web, retrieve relevant documents, and synthesize a concise summary",
    status: "active",
    trigger_type: "manual",
    version: 2,
    created_at: new Date(Date.now() - 14 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 3 * 86400000).toISOString(),
    nodes: [
      {
        id: "start",
        type: "start",
        position: { x: 50, y: 200 },
        data: { label: "Start" },
      },
      {
        id: "rag-1",
        type: "rag",
        position: { x: 250, y: 200 },
        data: { label: "Knowledge Base Lookup", top_k: 5 },
      },
      {
        id: "tool-1",
        type: "tool",
        position: { x: 450, y: 100 },
        data: { label: "Web Search", tool_name: "web_search" },
      },
      {
        id: "agent-1",
        type: "agent",
        position: { x: 650, y: 200 },
        data: {
          label: "Research Agent",
          model: "deepseek/deepseek-r1:free",
          system_prompt:
            "Synthesize the provided context into a clear, concise summary with citations.",
        },
      },
      {
        id: "end",
        type: "end",
        position: { x: 850, y: 200 },
        data: { label: "End" },
      },
    ],
    edges: [
      { id: "e1", source: "start", target: "rag-1" },
      { id: "e2", source: "rag-1", target: "tool-1" },
      { id: "e3", source: "tool-1", target: "agent-1" },
      { id: "e4", source: "agent-1", target: "end" },
    ],
  },
  {
    id: "demo-wf-003",
    name: "Daily Report Generator",
    description:
      "Scheduled workflow that pulls data, analyses trends, and sends a Slack summary",
    status: "active",
    trigger_type: "scheduled",
    version: 1,
    created_at: new Date(Date.now() - 21 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    nodes: [
      {
        id: "start",
        type: "start",
        position: { x: 50, y: 200 },
        data: { label: "Daily Trigger", cron: "0 9 * * 1-5" },
      },
      {
        id: "tool-1",
        type: "tool",
        position: { x: 250, y: 200 },
        data: { label: "Fetch Metrics", tool_name: "http_request" },
      },
      {
        id: "agent-1",
        type: "agent",
        position: { x: 450, y: 200 },
        data: {
          label: "Analyst Agent",
          model: "qwen/qwen3-235b-a22b:free",
          system_prompt:
            "Analyse the provided metrics and generate a concise executive summary.",
        },
      },
      {
        id: "memory-1",
        type: "memory",
        position: { x: 650, y: 200 },
        data: { label: "Store to Memory", memory_type: "long_term" },
      },
      {
        id: "end",
        type: "end",
        position: { x: 850, y: 200 },
        data: { label: "End" },
      },
    ],
    edges: [
      { id: "e1", source: "start", target: "tool-1" },
      { id: "e2", source: "tool-1", target: "agent-1" },
      { id: "e3", source: "agent-1", target: "memory-1" },
      { id: "e4", source: "memory-1", target: "end" },
    ],
  },
];

// ---------------------------------------------------------------------------
// Demo Agents
// ---------------------------------------------------------------------------
export const DEMO_AGENTS: Agent[] = [
  {
    id: "demo-agent-001",
    name: "Research Agent",
    description:
      "Searches the web and knowledge base to answer complex research questions",
    agent_type: "research",
    model: "meta-llama/llama-3.3-70b-instruct:free",
    system_prompt:
      "You are an expert research assistant. Search the web and internal knowledge base to provide accurate, cited answers.",
    tools: ["web_search", "rag_search"],
    created_at: new Date(Date.now() - 10 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 86400000).toISOString(),
  },
  {
    id: "demo-agent-002",
    name: "Code Review Agent",
    description: "Reviews code for bugs, security issues, and style violations",
    agent_type: "executor",
    model: "deepseek/deepseek-r1:free",
    system_prompt:
      "You are a senior software engineer. Review code carefully for bugs, security vulnerabilities, and adherence to best practices.",
    tools: ["code_executor"],
    created_at: new Date(Date.now() - 8 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
  },
  {
    id: "demo-agent-003",
    name: "Customer Support Agent",
    description: "Handles customer inquiries and routes escalations appropriately",
    agent_type: "supervisor",
    model: "google/gemma-3-27b-it:free",
    system_prompt:
      "You are a friendly, professional customer support representative. Resolve issues with empathy and clarity.",
    tools: ["web_search"],
    created_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
  },
  {
    id: "demo-agent-004",
    name: "Data Analyst Agent",
    description:
      "Interprets datasets, generates insights, and produces structured reports",
    agent_type: "research",
    model: "qwen/qwen3-235b-a22b:free",
    system_prompt:
      "You are a data analyst. Interpret provided data, identify trends, and produce clear, actionable reports.",
    tools: ["code_executor", "http_request"],
    created_at: new Date(Date.now() - 3 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
  },
];

// ---------------------------------------------------------------------------
// Demo Documents (Knowledge Base)
// ---------------------------------------------------------------------------
export const DEMO_DOCUMENTS: Document[] = [
  {
    id: "demo-doc-001",
    name: "NexusFlow Product Guide.pdf",
    file_url: "#",
    file_type: "pdf",
    file_size: 2457600, // ~2.4 MB
    status: "completed",
    chunk_count: 142,
    created_at: new Date(Date.now() - 12 * 86400000).toISOString(),
  },
  {
    id: "demo-doc-002",
    name: "API Integration Handbook.md",
    file_url: "#",
    file_type: "markdown",
    file_size: 81920, // ~80 KB
    status: "completed",
    chunk_count: 38,
    created_at: new Date(Date.now() - 9 * 86400000).toISOString(),
  },
  {
    id: "demo-doc-003",
    name: "Customer FAQ Database.txt",
    file_url: "#",
    file_type: "txt",
    file_size: 163840, // ~160 KB
    status: "completed",
    chunk_count: 67,
    created_at: new Date(Date.now() - 6 * 86400000).toISOString(),
  },
];

// ---------------------------------------------------------------------------
// Demo Memory
// ---------------------------------------------------------------------------
export const DEMO_MEMORY: Memory[] = [
  {
    id: "demo-mem-001",
    content:
      "User requested analysis of Q4 sales data. Focus areas: APAC growth, churn rate reduction, and new product uptake.",
    memory_type: "short_term",
    created_at: new Date(Date.now() - 1 * 3600000).toISOString(),
  },
  {
    id: "demo-mem-002",
    content:
      "Customer prefers concise bullet-point summaries over long prose. Always include a TL;DR at the top.",
    memory_type: "long_term",
    created_at: new Date(Date.now() - 4 * 86400000).toISOString(),
  },
  {
    id: "demo-mem-003",
    content:
      "Successfully resolved payment gateway integration issue on 2024-11-14. Root cause: API key rotation without secret manager update.",
    memory_type: "episodic",
    created_at: new Date(Date.now() - 8 * 86400000).toISOString(),
  },
  {
    id: "demo-mem-004",
    content:
      "Project milestone: NexusFlow v2.0 public launch is scheduled for Q1 2025. Key deliverables: multi-tenant RBAC, streaming execution, marketplace integrations.",
    memory_type: "long_term",
    created_at: new Date(Date.now() - 11 * 86400000).toISOString(),
  },
  {
    id: "demo-mem-005",
    content:
      "Current task: Generate weekly performance report for the executive team. Include KPIs: DAU, retention rate, revenue, and NPS.",
    memory_type: "short_term",
    created_at: new Date(Date.now() - 30 * 60000).toISOString(),
  },
];

// ---------------------------------------------------------------------------
// Demo Approvals
// ---------------------------------------------------------------------------
export const DEMO_APPROVALS: HumanApproval[] = [
  {
    id: "demo-appr-001",
    execution_id: "exec-7f3a2b1c-9d4e-4f5a-8b2c-1d3e5f7a9b0c",
    message:
      "Research Agent identified a critical security vulnerability in the authentication module. Proposed fix: patch JWT validation logic. Deploy to production?",
    context: {
      workflow: "Customer Support Bot",
      node: "Security Review",
      risk_level: "high",
      suggested_action: "Apply patch to JWT middleware and redeploy API service.",
    },
    status: "pending",
    created_at: new Date(Date.now() - 45 * 60000).toISOString(),
  },
  {
    id: "demo-appr-002",
    execution_id: "exec-2a4b6c8d-0e2f-4a6b-8c0d-2e4f6a8b0c2e",
    message:
      "Daily Report Generator is ready to send the weekly summary to 847 customer records via email. This action cannot be undone. Confirm batch send?",
    context: {
      workflow: "Daily Report Generator",
      node: "Batch Email Sender",
      recipients: 847,
      template: "weekly_performance_summary_v3",
    },
    status: "pending",
    created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
  },
];

// ---------------------------------------------------------------------------
// Demo Analytics
// ---------------------------------------------------------------------------
function daysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().split("T")[0];
}

export const DEMO_ANALYTICS: AnalyticsDashboard = {
  total_executions: 1247,
  successful_executions: 1189,
  failed_executions: 58,
  active_workflows: 8,
  total_tokens: 4280000,
  total_cost: 0,
  executions_by_day: [
    { day: daysAgo(13), total: 68, successful: 64 },
    { day: daysAgo(12), total: 92, successful: 88 },
    { day: daysAgo(11), total: 75, successful: 70 },
    { day: daysAgo(10), total: 110, successful: 107 },
    { day: daysAgo(9), total: 87, successful: 83 },
    { day: daysAgo(8), total: 95, successful: 91 },
    { day: daysAgo(7), total: 120, successful: 116 },
    { day: daysAgo(6), total: 98, successful: 92 },
    { day: daysAgo(5), total: 134, successful: 128 },
    { day: daysAgo(4), total: 89, successful: 85 },
    { day: daysAgo(3), total: 102, successful: 99 },
    { day: daysAgo(2), total: 78, successful: 73 },
    { day: daysAgo(1), total: 115, successful: 113 },
    { day: daysAgo(0), total: 84, successful: 80 },
  ],
  cost_by_day: [
    { day: daysAgo(13), cost: 0 },
    { day: daysAgo(12), cost: 0 },
    { day: daysAgo(11), cost: 0 },
    { day: daysAgo(10), cost: 0 },
    { day: daysAgo(9), cost: 0 },
    { day: daysAgo(8), cost: 0 },
    { day: daysAgo(7), cost: 0 },
    { day: daysAgo(6), cost: 0 },
    { day: daysAgo(5), cost: 0 },
    { day: daysAgo(4), cost: 0 },
    { day: daysAgo(3), cost: 0 },
    { day: daysAgo(2), cost: 0 },
    { day: daysAgo(1), cost: 0 },
    { day: daysAgo(0), cost: 0 },
  ],
  token_usage_by_model: [
    {
      model: "meta-llama/llama-3.3-70b-instruct:free",
      tokens: 2100000,
      cost: 0,
    },
    { model: "deepseek/deepseek-r1:free", tokens: 980000, cost: 0 },
    { model: "google/gemma-3-27b-it:free", tokens: 640000, cost: 0 },
    { model: "qwen/qwen3-235b-a22b:free", tokens: 380000, cost: 0 },
    { model: "mistralai/mistral-7b-instruct:free", tokens: 180000, cost: 0 },
  ],
  top_workflows: [
    {
      workflow_id: "demo-wf-001",
      name: "Customer Support Bot",
      executions: 524,
    },
    {
      workflow_id: "demo-wf-002",
      name: "Research & Summarize",
      executions: 418,
    },
    {
      workflow_id: "demo-wf-003",
      name: "Daily Report Generator",
      executions: 305,
    },
  ],
  agent_performance: [
    {
      agent_type: "research",
      total_runs: 482,
      total: 482,
      success_rate: 96.5,
    },
    {
      agent_type: "executor",
      total_runs: 358,
      total: 358,
      success_rate: 94.1,
    },
    {
      agent_type: "supervisor",
      total_runs: 241,
      total: 241,
      success_rate: 98.3,
    },
    {
      agent_type: "custom",
      total_runs: 166,
      total: 166,
      success_rate: 91.0,
    },
  ],
};
