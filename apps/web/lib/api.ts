/**
 * API client: typed fetch wrapper for the NexusFlow backend.
 * Auth tokens are passed explicitly via the token option from authClient.token().
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function getAuthHeaders(): Promise<Record<string, string>> {
  return {};
}

type ApiOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  body?: unknown;
  token?: string;
};

async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (options.token) {
    headers["Authorization"] = `Bearer ${options.token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ---- Workflow endpoints ----
export const workflowsApi = {
  list: (token: string) =>
    apiFetch<Workflow[]>("/workflows", { token }),
  get: (id: string, token: string) =>
    apiFetch<Workflow>(`/workflows/${id}`, { token }),
  create: (body: Partial<Workflow>, token: string) =>
    apiFetch<Workflow>("/workflows", { method: "POST", body, token }),
  update: (id: string, body: Partial<Workflow>, token: string) =>
    apiFetch<Workflow>(`/workflows/${id}`, { method: "PUT", body, token }),
  delete: (id: string, token: string) =>
    apiFetch<void>(`/workflows/${id}`, { method: "DELETE", token }),
  execute: (id: string, input: Record<string, unknown>, token: string) =>
    apiFetch<ExecutionResponse>(`/workflows/${id}/execute`, { method: "POST", body: { input }, token }),
  executions: (id: string, token: string) =>
    apiFetch<ExecutionResponse[]>(`/workflows/${id}/executions`, { token }),
};

// ---- Agent endpoints ----
export const agentsApi = {
  list: (token: string) => apiFetch<Agent[]>("/agents", { token }),
  create: (body: Partial<Agent>, token: string) =>
    apiFetch<Agent>("/agents", { method: "POST", body, token }),
  update: (id: string, body: Partial<Agent>, token: string) =>
    apiFetch<Agent>(`/agents/${id}`, { method: "PUT", body, token }),
  delete: (id: string, token: string) =>
    apiFetch<void>(`/agents/${id}`, { method: "DELETE", token }),
  run: (id: string, input: { task: string; [k: string]: unknown }, token: string) =>
    apiFetch<AgentRunResponse>(`/agents/${id}/run`, { method: "POST", body: input, token }),
};

// ---- Document endpoints ----
export const documentsApi = {
  list: (token: string) => apiFetch<Document[]>("/documents", { token }),
  create: (body: { name: string; file_url: string; mime_type?: string; file_type?: string; file_size?: number }, token: string) =>
    apiFetch<Document>("/documents", { method: "POST", body, token }),
  delete: (id: string, token: string) =>
    apiFetch<void>(`/documents/${id}`, { method: "DELETE", token }),
};

// ---- RAG endpoints ----
export const ragApi = {
  search: (query: string, top_k: number, token: string) =>
    apiFetch<RAGSearchResponse>("/rag/search", { method: "POST", body: { query, top_k, use_hybrid: true }, token }),
};

// ---- Analytics endpoints ----
export const analyticsApi = {
  dashboard: (days: number, token: string) =>
    apiFetch<AnalyticsDashboard>(`/analytics/dashboard?days=${days}`, { token }),
};

// ---- Tools endpoints ----
export const toolsApi = {
  listBuiltIn: (token: string) => apiFetch<BuiltInTool[]>("/tools/built-in", { token }),
  execute: (tool_name: string, input: Record<string, unknown>, token: string) =>
    apiFetch<ToolExecuteResponse>("/tools/execute", { method: "POST", body: { tool_name, input }, token }),
};

// ---- Memory endpoints ----
export const memoryApi = {
  list: (token: string) => apiFetch<Memory[]>("/memory", { token }),
  create: (content: string, memory_type: string, token: string) =>
    apiFetch<Memory>("/memory", { method: "POST", body: { content, memory_type }, token }),
  delete: (id: string, token: string) =>
    apiFetch<void>(`/memory/${id}`, { method: "DELETE", token }),
};

// ---- Approval endpoints ----
export const approvalsApi = {
  list: (token: string) => apiFetch<HumanApproval[]>("/approvals", { token }),
  action: (id: string, action: "approved" | "rejected", comment: string | undefined, token: string) =>
    apiFetch<HumanApproval>(`/approvals/${id}/action`, { method: "POST", body: { action, comment }, token }),
};

// ---- Demo seed ----
export const demoApi = {
  seed: (token: string) =>
    apiFetch<{ seeded: boolean; reason?: string; summary?: Record<string, number> }>(
      "/demo/seed",
      { method: "POST", token },
    ),
};

// ---- Prompt Studio ----
export const promptStudioApi = {
  run: (body: PromptRunRequest, token: string) =>
    apiFetch<PromptRunResponse>("/prompt-studio/run", { method: "POST", body, token }),
};

// ---- Types ----
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  version: number;
  status: string;
  trigger_type: string;
  created_at: string;
  updated_at: string;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
}

export interface ExecutionResponse {
  execution_id: string;
  workflow_id: string;
  status: string;
  stream_url: string;
}

export interface Agent {
  id: string;
  name: string;
  description?: string;
  agent_type: string;
  model: string;
  system_prompt?: string;
  tools: string[];
  created_at: string;
  updated_at: string;
}

export interface AgentRunResponse {
  execution_id: string;
  output: string;
  reasoning_trace: string[];
  latency_ms: number;
  model: string;
}

export interface Document {
  id: string;
  name: string;
  file_url: string;
  file_type: string;
  file_size: number;
  status: string;
  chunk_count?: number;
  created_at: string;
}

export interface RAGSearchResponse {
  query: string;
  results: RAGResult[];
  total: number;
}

export interface RAGResult {
  chunk_id: string;
  document_name: string;
  content: string;
  similarity: number;
}

export interface AnalyticsDashboard {
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  active_workflows: number;
  total_tokens: number;
  total_cost: number;
  executions_by_day: { day: string; total: number; successful: number }[];
  token_usage_by_model: { model: string; tokens: number; cost: number }[];
  top_workflows: { workflow_id: string; name: string; executions: number }[];
  agent_performance: { agent_type: string; total_runs: number; total: number; success_rate: number }[];
  cost_by_day: { day: string; cost: number }[];
}

export interface Memory {
  id: string;
  content: string;
  memory_type: string;
  created_at: string;
}

export interface HumanApproval {
  id: string;
  execution_id: string;
  message: string;
  context?: unknown;
  status: string;
  created_at: string;
}

export interface BuiltInTool {
  name: string;
  description: string;
}

export interface ToolExecuteResponse {
  tool_name: string;
  output: unknown;
  success: boolean;
  error?: string;
  latency_ms: number;
}

export interface PromptRunRequest {
  user_prompt: string;
  system_prompt?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  use_rag?: boolean;
  rag_query?: string;
}

export interface PromptRunResponse {
  output: string;
  model: string;
  latency_ms: number;
  rag_context_used: boolean;
  usage: { input_tokens?: number; output_tokens?: number };
}
