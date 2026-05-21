"use client";

import { useEffect, useState, useCallback } from "react";
import { useUser } from "@stackframe/stack";
import { useParams } from "next/navigation";
import type { Node, Edge } from "@xyflow/react";
import { WorkflowCanvas } from "@/components/workflow/WorkflowCanvas";
import { workflowsApi, type Workflow } from "@/lib/api";
import { useSSE } from "@/hooks/useSSE";
import { CheckCircle, XCircle, Loader2, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";

function SSEConsole({
  executionId,
  token,
  onClose,
}: {
  executionId: string;
  token: string;
  onClose: () => void;
}) {
  const { events, isConnected, isDone } = useSSE(executionId, token);

  return (
    <div className="fixed inset-x-0 bottom-0 bg-slate-900 border-t border-slate-800 z-50 h-64 flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white">
            Execution: {executionId.slice(0, 8)}…
          </span>
          {!isDone && isConnected && (
            <Loader2 className="h-3.5 w-3.5 animate-spin text-purple-400" />
          )}
          {isDone && <Badge variant="success">Done</Badge>}
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white">
          <X className="h-4 w-4" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-1 font-mono text-xs">
        {events.map((e, i) => (
          <div
            key={i}
            className={`flex gap-2 ${e.type === "error" ? "text-red-400" : e.type === "completed" ? "text-green-400" : "text-slate-300"}`}
          >
            <span className="text-slate-600 shrink-0">
              {new Date(e.timestamp ?? "").toLocaleTimeString()}
            </span>
            <span className="text-slate-500 shrink-0">[{e.type}]</span>
            <span className="break-all">
              {typeof e.data === "string" ? e.data : JSON.stringify(e.data)}
            </span>
          </div>
        ))}
        {events.length === 0 && (
          <p className="text-slate-600">Waiting for events…</p>
        )}
      </div>
    </div>
  );
}

export default function EditWorkflowPage() {
  const { id } = useParams<{ id: string }>();
  const user = useUser();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [token, setToken] = useState("");
  const [executionId, setExecutionId] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const t = await user?.getAuthJson();
      if (!t?.accessToken) return;
      setToken(t.accessToken);
      const wf = await workflowsApi.get(id, t.accessToken);
      setWorkflow(wf);
      setLoading(false);
    };
    if (user) load();
  }, [user, id]);

  const handleSave = useCallback(
    async (nodes: Node[], edges: Edge[]) => {
      if (!workflow) return;
      setSaving(true);
      try {
        const t = await user?.getAuthJson();
        if (!t?.accessToken) return;
        await workflowsApi.update(
          id,
          {
            name: workflow.name,
            nodes: nodes as unknown as Workflow["nodes"],
            edges: edges as unknown as Workflow["edges"],
          },
          t.accessToken,
        );
      } catch (err: unknown) {
        alert(err instanceof Error ? err.message : "Save failed");
      } finally {
        setSaving(false);
      }
    },
    [workflow, user, id],
  );

  const handleExecute = useCallback(async () => {
    try {
      const t = await user?.getAuthJson();
      if (!t?.accessToken) return;
      const result = await workflowsApi.execute(id, {}, t.accessToken);
      setExecutionId(result.execution_id);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Execution failed");
    }
  }, [user, id]);

  if (loading) {
    return (
      <div className="h-[calc(100vh-2rem)] -m-8 flex items-center justify-center bg-slate-950">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </div>
    );
  }

  return (
    <>
      <div
        className={`h-[calc(100vh-2rem)] -m-8 overflow-hidden ${executionId ? "pb-64" : ""}`}
      >
        <WorkflowCanvas
          initialNodes={(workflow?.nodes as Node[] | undefined) ?? []}
          initialEdges={(workflow?.edges as Edge[] | undefined) ?? []}
          workflowName={workflow?.name ?? ""}
          onNameChange={(name) => setWorkflow((w) => (w ? { ...w, name } : w))}
          onSave={handleSave}
          onExecute={handleExecute}
          saving={saving}
        />
      </div>
      {executionId && token && (
        <SSEConsole
          executionId={executionId}
          token={token}
          onClose={() => setExecutionId(null)}
        />
      )}
    </>
  );
}
