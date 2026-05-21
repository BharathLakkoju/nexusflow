<div align="center">

<h1>
  <img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Brain/3D/brain_3d.png" width="48" height="48" alt="brain" />
  &nbsp;NexusFlow AI
</h1>

<p><strong>Visual multi-agent AI orchestration — design, deploy, and monitor AI workflows without writing infrastructure.</strong></p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.4-7C3AED?logo=python&logoColor=white)](https://www.langchain.com/langgraph)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)](https://neon.tech)
[![Deploy on Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://vercel.com)

<br/>

![NexusFlow AI — Visual Workflow Canvas](https://placehold.co/1200x600/1C1006/F5EFE6?text=NexusFlow+AI+%E2%80%94+Visual+Multi-Agent+Orchestration&font=montserrat)

</div>

---

## ✨ What is NexusFlow AI?

NexusFlow AI is an **open-source multi-agent AI orchestration platform** that lets you visually compose, deploy, and monitor teams of AI agents — without touching infrastructure code.

Think of it as the **Figma for AI agent workflows**: drag-and-drop nodes onto a canvas, wire agents together into a DAG, upload your knowledge base, and watch your AI team execute in real time.

- 🧠 **4 specialized agent roles** — Researcher, Planner, Executor, Critic
- 🎨 **Visual canvas** — 11 node types, drag-and-drop powered by React Flow
- 📚 **RAG knowledge base** — semantic retrieval over PDFs, Docs, CSVs, URLs
- 🔍 **Full observability** — token costs, execution traces, success rates per run
- 🔐 **Enterprise-ready** — RBAC, org management, human-in-the-loop approvals
- ⚡ **Real-time streaming** — agent thoughts streamed live via SSE

---

## 🏗️ Architecture

```
nexusflow/
├── apps/
│   ├── web/          # Next.js 16 + React 19 frontend (Vercel)
│   └── api/          # FastAPI + LangGraph backend (Render / Docker)
└── turbo.json        # Turborepo monorepo config
```

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16, React 19, React Flow (XYFlow), Framer Motion, Tailwind CSS, Radix UI, Zustand |
| **Backend** | FastAPI, LangGraph, LangChain, SQLAlchemy (async), Alembic |
| **Database** | Neon PostgreSQL + pgvector (semantic search) |
| **Auth** | Neon Auth (JWT / OAuth — email + Google) |
| **Background Jobs** | Inngest (durable function queue) |
| **Real-time** | Upstash Redis + Server-Sent Events |
| **AI Gateway** | OpenRouter (GPT-4o, Claude 3.5, Gemini, Llama 3…) |
| **File Storage** | Vercel Blob |
| **Web Search** | Tavily / DuckDuckGo (automatic fallback) |
| **Observability** | OpenTelemetry (FastAPI + SQLAlchemy instrumentation) |

---

## 🚀 Features

### 🎨 Visual Workflow Builder
Build directed acyclic graphs (DAGs) of AI agents on a drag-and-drop canvas. 11 node types include Trigger, Researcher, Planner, Executor, Critic, Tool, RAG Retrieval, Memory Read/Write, Condition, and Output.

### 🤖 Multi-Agent Orchestration (LangGraph)
Four built-in agent roles collaborate via a graph-based execution engine:

| Agent | Role |
|---|---|
| **Researcher** | Web search, document retrieval, fact-finding |
| **Planner** | Decomposes objectives into actionable sub-tasks |
| **Executor** | Runs tools, calls APIs, writes outputs |
| **Critic** | Reviews results, flags quality issues, requests retries |

A **Supervisor** agent coordinates the team and decides when the goal is achieved.

### 📚 RAG Knowledge Base
Upload documents in any format — PDF, DOCX, CSV, XLSX, TXT, HTML, Markdown. The ingestion pipeline chunks, embeds (OpenAI embeddings), and stores them in Neon's `pgvector` extension. Agents retrieve semantically relevant context at runtime automatically.

### 🔍 Full Observability Dashboard
- Token usage and cost per agent run
- Execution timeline and step-by-step traces
- Success / failure rates per workflow
- Live streaming of agent reasoning and tool calls

### 🛡️ Enterprise Security
- **RBAC** — owner, admin, member roles per organization
- **Human-in-the-loop** — agents can pause and await human approval before executing sensitive actions (e.g., sending emails, modifying databases)
- **Multi-tenant** data isolation per organization
- **Rate limiting** via SlowAPI (100 req/min default)
- **JWT authentication** with JWKS verification

### 🔧 Prompt Studio
Craft, test, and version-control system prompts for each agent. Edit prompts live and see results without redeploying.

### 🔑 API Key Management
Generate scoped API keys for programmatic workflow triggering. Integrate NexusFlow into your existing CI/CD pipelines or backend services.

---

## 🛠️ Local Development

### Prerequisites

- Node.js ≥ 20
- Python ≥ 3.11
- pnpm ≥ 9
- A [Neon](https://neon.tech) database (free tier works)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/nexusflow.git
cd nexusflow
```

### 2. Install frontend dependencies

```bash
pnpm install
```

### 3. Set up the backend

```bash
cd apps/api

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 4. Configure environment variables

**Backend** — copy and fill in `apps/api/.env`:
```bash
cp apps/api/.env.example apps/api/.env
```

**Frontend** — copy and fill in `apps/web/.env.local`:
```bash
cp apps/web/.env.example apps/web/.env.local
```

See [`.env.example`](apps/api/.env.example) for all required variables and where to get them.

### 5. Run database migrations

```bash
cd apps/api
alembic upgrade head
```

### 6. Start everything

```bash
# From repo root — starts both apps in parallel
pnpm dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## 🌐 Deployment

Full step-by-step deployment to **Neon + Render + Vercel** (all free tiers) is documented in [`DEPLOYMENT.md`](DEPLOYMENT.md).

**TL;DR:**

| Component | Platform | Time |
|---|---|---|
| Database + Auth | [Neon](https://neon.tech) | ~5 min |
| Backend API | [Render](https://render.com) | ~10 min |
| Frontend | [Vercel](https://vercel.com) | ~5 min |

Total cost on free tiers: **$0/month** (+ OpenRouter usage, ~$0.15 per 1M tokens with GPT-4o Mini).

---

## 🔌 API Reference

The backend exposes a versioned REST API under `/api/v1`. Interactive Swagger docs are available at `/docs` in development.

| Router | Endpoint prefix | Description |
|---|---|---|
| Auth | `/api/v1/auth` | Token validation, session info |
| Organizations | `/api/v1/organizations` | CRUD, member management, RBAC |
| Workflows | `/api/v1/workflows` | Create, run, list, delete workflows |
| Agents | `/api/v1/agents` | Agent configuration per workflow |
| Documents | `/api/v1/documents` | Upload and manage RAG documents |
| RAG | `/api/v1/rag` | Semantic search / retrieval |
| Memory | `/api/v1/memory` | Persistent agent memory store |
| Tools | `/api/v1/tools` | Custom tool registration |
| Stream | `/api/v1/stream` | SSE stream for live agent output |
| Approvals | `/api/v1/approvals` | Human-in-the-loop approval queue |
| Prompt Studio | `/api/v1/prompt-studio` | Prompt templates and versioning |
| Analytics | `/api/v1/analytics` | Usage metrics and run history |
| Keys | `/api/v1/keys` | API key management |

**Health check:**
```
GET /health
→ { "status": "ok", "version": "1.0.0" }
```

---

## ⚙️ Environment Variables

### Backend (`apps/api/.env`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Neon PostgreSQL connection string |
| `NEON_AUTH_JWKS_URL` | ✅ | Neon Auth JWKS endpoint for JWT verification |
| `UPSTASH_REDIS_REST_URL` | ✅ | Upstash Redis REST URL |
| `UPSTASH_REDIS_REST_TOKEN` | ✅ | Upstash Redis REST token |
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key (`sk-or-v1-...`) |
| `INNGEST_EVENT_KEY` | ✅ | Inngest event key |
| `INNGEST_SIGNING_KEY` | ✅ | Inngest signing key |
| `SECRET_KEY` | ✅ | 64-char hex secret for internal signing |
| `FRONTEND_URL` | ✅ | Frontend origin for CORS |
| `TAVILY_API_KEY` | ⬜ | Tavily web search (DuckDuckGo used as fallback) |
| `BLOB_READ_WRITE_TOKEN` | ⬜ | Vercel Blob token (if backend reads uploaded files) |

### Frontend (`apps/web/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend API base URL (`/api/v1`) |
| `NEON_AUTH_BASE_URL` | ✅ | Neon Auth base URL |
| `NEON_AUTH_COOKIE_SECRET` | ✅ | 32-char base64 secret for auth cookies |
| `BLOB_READ_WRITE_TOKEN` | ✅ | Vercel Blob token for file uploads |

---

## 🗺️ Roadmap

- [ ] **Scheduled workflows** — cron-based triggers
- [ ] **Webhook triggers** — fire workflows from external events
- [ ] **More LLM providers** — direct Anthropic, Google, Groq integrations
- [ ] **Custom tool builder** — define tools via UI with no code
- [ ] **Workflow marketplace** — share and clone community templates
- [ ] **Slack / Discord notifications** — agent completion alerts
- [ ] **Export to code** — generate LangGraph Python from visual canvas

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork this repo
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ using [FastAPI](https://fastapi.tiangolo.com) · [LangGraph](https://www.langchain.com/langgraph) · [Next.js](https://nextjs.org) · [Neon](https://neon.tech)

⭐ **Star this repo if NexusFlow saves you time!**

</div>
