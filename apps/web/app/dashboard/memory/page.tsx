"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/auth/hooks";
import { Brain, Trash2, Search, Loader2 } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface MemoryEntry {
  id: string;
  agent_id: string;
  memory_type: string;
  content: string;
  created_at: string;
  metadata?: Record<string, unknown>;
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

export default function MemoryPage() {
  const user = useUser();
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [token, setToken] = useState("");

  const load = async () => {
    const t = await user?.getAuthJson();
    if (!t?.accessToken) return;
    setToken(t.accessToken);
    try {
      const list = await apiFetch<MemoryEntry[]>("/memory", t.accessToken);
      setMemories(list);
    } catch {
      setMemories([]);
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
      await apiFetch(`/memory/${id}`, token, { method: "DELETE" });
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch {
      // silent
    }
  };

  const filtered = memories.filter(
    (m) =>
      m.content.toLowerCase().includes(search.toLowerCase()) ||
      m.memory_type.toLowerCase().includes(search.toLowerCase()),
  );

  const typeColor: Record<string, string> = {
    short_term: "bg-brown-200/60 text-brown-700",
    long_term: "bg-brown-300/60 text-brown-800",
    episodic: "bg-brown-400/40 text-brown-900",
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-800 tracking-tighter text-brown-900">
          Memory
        </h1>
        <p className="text-brown-500 text-sm mt-1">
          Agent memory entries across all sessions.
        </p>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-brown-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search memories…"
          className="w-full pl-9 pr-4 py-2.5 bg-brown-100 border border-brown-200 rounded-xl text-sm text-brown-800 placeholder:text-brown-400 focus:outline-none focus:ring-2 focus:ring-brown-300"
        />
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center gap-2 text-brown-400 text-sm py-8">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading memories…
        </div>
      ) : filtered.length === 0 ? (
        <div className="py-16 text-center border border-dashed border-brown-200 rounded-2xl bg-brown-100/40">
          <Brain className="h-10 w-10 text-brown-300 mx-auto mb-3" />
          <h3 className="text-base font-600 text-brown-700 mb-1">
            No memory entries
          </h3>
          <p className="text-sm text-brown-500 max-w-xs mx-auto">
            {search
              ? "No entries match your search."
              : "Agents will store memory here as they run."}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((entry) => (
            <div
              key={entry.id}
              className="bg-brown-100 border border-brown-200 rounded-xl p-5 flex gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2.5 mb-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      typeColor[entry.memory_type] ??
                      "bg-brown-200 text-brown-700"
                    }`}
                  >
                    {entry.memory_type.replace("_", " ")}
                  </span>
                  <span className="text-xs text-brown-400">
                    {formatDate(entry.created_at)}
                  </span>
                </div>
                <p className="text-sm text-brown-700 leading-relaxed line-clamp-3">
                  {entry.content}
                </p>
                {entry.agent_id && (
                  <p className="text-xs text-brown-400 mt-2">
                    Agent: {entry.agent_id.slice(0, 8)}…
                  </p>
                )}
              </div>
              <button
                onClick={() => handleDelete(entry.id)}
                className="text-brown-400 hover:text-red-500 transition-colors shrink-0"
                aria-label="Delete memory"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
