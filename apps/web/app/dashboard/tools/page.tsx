"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/auth/hooks";
import {
  Wrench,
  Plus,
  Trash2,
  Globe,
  Code,
  FileSearch,
  Loader2,
} from "lucide-react";
import { formatDate } from "@/lib/utils";

interface Tool {
  id: string;
  name: string;
  tool_type: string;
  description?: string;
  created_at: string;
  config: Record<string, unknown>;
}

async function apiFetch<T>(
  path: string,
  token: string,
  init?: RequestInit,
): Promise<T> {
  const base =
    process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
  const r = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers ?? {}),
    },
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

const TOOL_ICONS: Record<string, React.ElementType> = {
  http: Globe,
  web_search: FileSearch,
  code_executor: Code,
};

const TOOL_COLORS: Record<string, string> = {
  http: "bg-brown-200/60 text-brown-700",
  web_search: "bg-brown-300/60 text-brown-800",
  code_executor: "bg-brown-400/40 text-brown-900",
};

export default function ToolsPage() {
  const user = useUser();
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState("");

  const load = async () => {
    const t = await user?.getAuthJson();
    if (!t?.accessToken) return;
    setToken(t.accessToken);
    try {
      const list = await apiFetch<Tool[]>("/tools", t.accessToken);
      setTools(list);
    } catch {
      setTools([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const handleDelete = async (id: string) => {
    if (!token) return;
    try {
      await apiFetch(`/tools/${id}`, token, { method: "DELETE" });
      setTools((prev) => prev.filter((t) => t.id !== id));
    } catch {
      // silent
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-800 tracking-tighter text-brown-900">
            Tools
          </h1>
          <p className="text-brown-500 text-sm mt-1">
            Custom tools available to your agents.
          </p>
        </div>
        <button className="inline-flex items-center gap-2 bg-brown-800 hover:bg-brown-900 text-brown-50 text-sm font-medium px-4 py-2.5 rounded-xl transition-all duration-200 active:scale-[0.98]">
          <Plus className="h-4 w-4" />
          Add Tool
        </button>
      </div>

      {/* Built-in tools info */}
      <div className="bg-brown-100 border border-brown-200 rounded-xl p-5">
        <div className="text-xs font-semibold text-brown-600 uppercase tracking-widest mb-3">
          Built-in tools
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            {
              icon: Globe,
              name: "HTTP Tool",
              desc: "Make arbitrary HTTP requests",
            },
            {
              icon: FileSearch,
              name: "Web Search",
              desc: "Search the web via Serper API",
            },
            {
              icon: Code,
              name: "Code Executor",
              desc: "Run Python in sandboxed environment",
            },
          ].map((t) => (
            <div
              key={t.name}
              className="flex items-start gap-3 bg-brown-50 border border-brown-200 rounded-lg p-3.5"
            >
              <div className="h-8 w-8 rounded-lg bg-brown-700/10 flex items-center justify-center shrink-0">
                <t.icon className="h-4 w-4 text-brown-600" />
              </div>
              <div>
                <div className="text-sm font-medium text-brown-800">
                  {t.name}
                </div>
                <div className="text-xs text-brown-500 mt-0.5">{t.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Custom tools */}
      <div>
        <div className="text-xs font-semibold text-brown-600 uppercase tracking-widest mb-3">
          Custom tools
        </div>
        {loading ? (
          <div className="flex items-center gap-2 text-brown-400 text-sm py-8">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading tools…
          </div>
        ) : tools.length === 0 ? (
          <div className="py-16 text-center border border-dashed border-brown-200 rounded-2xl bg-brown-100/40">
            <Wrench className="h-10 w-10 text-brown-300 mx-auto mb-3" />
            <h3 className="text-base font-600 text-brown-700 mb-1">
              No custom tools yet
            </h3>
            <p className="text-sm text-brown-500 max-w-xs mx-auto">
              Create custom HTTP, search, or code tools that agents can call
              during workflows.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {tools.map((tool) => {
              const Icon = TOOL_ICONS[tool.tool_type] ?? Wrench;
              return (
                <div
                  key={tool.id}
                  className="bg-brown-100 border border-brown-200 rounded-xl p-5 flex items-start gap-4"
                >
                  <div className="h-9 w-9 rounded-lg bg-brown-700/10 flex items-center justify-center shrink-0">
                    <Icon className="h-4 w-4 text-brown-700" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2.5 mb-1">
                      <span className="text-sm font-700 text-brown-900">
                        {tool.name}
                      </span>
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          TOOL_COLORS[tool.tool_type] ??
                          "bg-brown-200 text-brown-700"
                        }`}
                      >
                        {tool.tool_type}
                      </span>
                    </div>
                    {tool.description && (
                      <p className="text-xs text-brown-600 leading-relaxed">
                        {tool.description}
                      </p>
                    )}
                    <p className="text-xs text-brown-400 mt-1">
                      {formatDate(tool.created_at)}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(tool.id)}
                    className="text-brown-400 hover:text-red-500 transition-colors"
                    aria-label="Delete tool"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
