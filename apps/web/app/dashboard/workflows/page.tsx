"use client";

import { useEffect, useState } from "react";
import { useUser } from "@stackframe/stack";
import {
  Plus,
  GitBranch,
  Play,
  Edit,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { workflowsApi, type Workflow } from "@/lib/api";
import { formatDate } from "@/lib/utils";

const STATUS_ICON: Record<string, React.ReactNode> = {
  completed: <CheckCircle className="h-3.5 w-3.5 text-green-400" />,
  failed: <XCircle className="h-3.5 w-3.5 text-red-400" />,
  running: <Loader2 className="h-3.5 w-3.5 text-blue-400 animate-spin" />,
  pending: <Clock className="h-3.5 w-3.5 text-yellow-400" />,
  draft: <Clock className="h-3.5 w-3.5 text-slate-400" />,
  active: <CheckCircle className="h-3.5 w-3.5 text-green-400" />,
};

export default function WorkflowsPage() {
  const user = useUser();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [executing, setExecuting] = useState<string | null>(null);

  const load = async () => {
    try {
      const token = await user?.getAuthJson();
      if (!token?.accessToken) return;
      const list = await workflowsApi.list(token.accessToken);
      setWorkflows(list);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const handleExecute = async (id: string) => {
    try {
      setExecuting(id);
      const token = await user?.getAuthJson();
      if (!token?.accessToken) return;
      const result = await workflowsApi.execute(id, {}, token.accessToken);
      alert(`Execution started! ID: ${result.execution_id}`);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Execution failed");
    } finally {
      setExecuting(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this workflow?")) return;
    try {
      const token = await user?.getAuthJson();
      if (!token?.accessToken) return;
      await workflowsApi.delete(id, token.accessToken);
      setWorkflows((prev) => prev.filter((w) => w.id !== id));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const filtered = workflows.filter((w) =>
    w.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Workflows</h1>
          <p className="text-slate-400 text-sm mt-1">
            {workflows.length} workflows
          </p>
        </div>
        <Link href="/dashboard/workflows/new">
          <Button className="bg-purple-600 hover:bg-purple-700 gap-2">
            <Plus className="h-4 w-4" /> New Workflow
          </Button>
        </Link>
      </div>

      <Input
        placeholder="Search workflows..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="bg-slate-900 border-slate-700 text-white max-w-sm"
      />

      {loading ? (
        <div className="grid gap-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-24 bg-slate-800 animate-pulse rounded-lg"
            />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-12 text-center">
            <GitBranch className="h-12 w-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400 mb-4">
              No workflows yet. Build your first AI workflow!
            </p>
            <Link href="/dashboard/workflows/new">
              <Button className="bg-purple-600 hover:bg-purple-700">
                <Plus className="h-4 w-4 mr-2" /> Create Workflow
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {filtered.map((wf) => (
            <Card
              key={wf.id}
              className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors"
            >
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <GitBranch className="h-5 w-5 text-purple-400 shrink-0" />
                    <div>
                      <p className="font-medium text-white">{wf.name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex items-center gap-1">
                          {STATUS_ICON[wf.status] ?? null}
                          <span className="text-xs text-slate-400 capitalize">
                            {wf.status}
                          </span>
                        </div>
                        <span className="text-slate-700">·</span>
                        <span className="text-xs text-slate-500">
                          v{wf.version}
                        </span>
                        <span className="text-slate-700">·</span>
                        <span className="text-xs text-slate-500">
                          {formatDate(wf.updated_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleExecute(wf.id)}
                      disabled={executing === wf.id}
                      className="text-green-400 hover:text-green-300 hover:bg-green-900/20"
                    >
                      {executing === wf.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>
                    <Link href={`/dashboard/workflows/${wf.id}/edit`}>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-slate-400 hover:text-white"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(wf.id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-900/20"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
