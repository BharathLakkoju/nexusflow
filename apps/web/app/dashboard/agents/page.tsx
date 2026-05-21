"use client";

import { useEffect, useState } from "react";
import { useUser } from "@stackframe/stack";
import { Plus, Bot, Play, Edit, Trash2, Loader2, X, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { agentsApi, type Agent } from "@/lib/api";
import { useSSE } from "@/hooks/useSSE";
import { formatDate } from "@/lib/utils";

function AgentRunModal({
  agent,
  token,
  onClose,
}: {
  agent: Agent;
  token: string;
  onClose: () => void;
}) {
  const [task, setTask] = useState("");
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const { events, isDone } = useSSE(executionId ?? "", token);

  const run = async () => {
    if (!task.trim()) return;
    setRunning(true);
    try {
      const result = await agentsApi.run(agent.id, { task }, token);
      setExecutionId(result.execution_id);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Run failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-purple-400" />
            <h3 className="font-semibold text-white">{agent.name}</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-4 space-y-3 flex-1 overflow-y-auto">
          {!executionId ? (
            <div className="space-y-3">
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Describe the task for this agent..."
                rows={4}
                className="bg-slate-800 border-slate-700 text-white"
              />
              <Button
                onClick={run}
                disabled={running || !task.trim()}
                className="bg-purple-600 hover:bg-purple-700 gap-2"
              >
                {running ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                Run Agent
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <p className="text-sm text-slate-400">
                  Execution: {executionId.slice(0, 12)}…
                </p>
                {!isDone && (
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-purple-400" />
                )}
                {isDone && <Badge variant="success">Completed</Badge>}
              </div>
              <div className="bg-slate-950 rounded-lg p-3 font-mono text-xs space-y-1 max-h-64 overflow-y-auto">
                {events.map((e, i) => (
                  <div
                    key={i}
                    className={
                      e.type === "error"
                        ? "text-red-400"
                        : e.type === "completed"
                          ? "text-green-400"
                          : "text-slate-300"
                    }
                  >
                    <span className="text-slate-600">[{e.type}]</span>{" "}
                    {typeof e.data === "string"
                      ? e.data
                      : JSON.stringify(e.data)}
                  </div>
                ))}
                {events.length === 0 && (
                  <p className="text-slate-600">Waiting for events…</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AgentsPage() {
  const user = useUser();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState("");
  const [runTarget, setRunTarget] = useState<Agent | null>(null);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);

  const load = async () => {
    const t = await user?.getAuthJson();
    if (!t?.accessToken) return;
    setToken(t.accessToken);
    const list = await agentsApi.list(t.accessToken);
    setAgents(list);
    setLoading(false);
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const agent = await agentsApi.create(
        {
          name: newName,
          agent_type: "research",
          model: "openai/gpt-4o-mini",
          system_prompt: "You are a helpful AI assistant.",
        },
        token,
      );
      setAgents((prev) => [...prev, agent]);
      setNewName("");
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Create failed");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this agent?")) return;
    await agentsApi.delete(id, token);
    setAgents((prev) => prev.filter((a) => a.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Agents</h1>
          <p className="text-slate-400 text-sm mt-1">{agents.length} agents</p>
        </div>
      </div>

      {/* Quick create */}
      <div className="flex gap-2 max-w-sm">
        <Input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="New agent name..."
          className="bg-slate-900 border-slate-700 text-white"
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
        />
        <Button
          onClick={handleCreate}
          disabled={creating || !newName.trim()}
          className="bg-purple-600 hover:bg-purple-700 gap-2 shrink-0"
        >
          {creating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          Create
        </Button>
      </div>

      {loading ? (
        <div className="grid gap-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-20 bg-slate-800 animate-pulse rounded-lg"
            />
          ))}
        </div>
      ) : agents.length === 0 ? (
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-12 text-center">
            <Bot className="h-12 w-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">
              No agents yet. Create your first AI agent!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {agents.map((a) => (
            <Card
              key={a.id}
              className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors"
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Bot className="h-5 w-5 text-purple-400" />
                    <div>
                      <p className="font-medium text-white">{a.name}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Badge variant="secondary" className="text-[10px]">
                          {a.agent_type}
                        </Badge>
                        <span className="text-xs text-slate-500">
                          {a.model.split("/")[1]}
                        </span>
                        <span className="text-xs text-slate-600">
                          {formatDate(a.updated_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => setRunTarget(a)}
                      className="bg-green-600 hover:bg-green-700 gap-1"
                    >
                      <Play className="h-3.5 w-3.5" /> Run
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-red-400 hover:text-red-300"
                      onClick={() => handleDelete(a.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {runTarget && token && (
        <AgentRunModal
          agent={runTarget}
          token={token}
          onClose={() => setRunTarget(null)}
        />
      )}
    </div>
  );
}
