"use client";

import { useState, useCallback } from "react";
import { useUser } from "@/lib/auth/hooks";
import { useRouter } from "next/navigation";
import type { Node, Edge } from "@xyflow/react";
import { WorkflowCanvas } from "@/components/workflow/WorkflowCanvas";
import { workflowsApi } from "@/lib/api";

// Default starter nodes
const DEFAULT_NODES: Node[] = [
  {
    id: "start-1",
    type: "custom",
    position: { x: 100, y: 200 },
    data: { nodeType: "start", label: "Start" },
  },
  {
    id: "agent-1",
    type: "custom",
    position: { x: 360, y: 200 },
    data: {
      nodeType: "agent",
      label: "AI Agent",
      model: "openai/gpt-4o-mini",
      prompt: "{{input}}",
    },
  },
  {
    id: "end-1",
    type: "custom",
    position: { x: 620, y: 200 },
    data: { nodeType: "end", label: "End" },
  },
];

const DEFAULT_EDGES: Edge[] = [
  {
    id: "e-start-agent",
    source: "start-1",
    target: "agent-1",
    type: "smoothstep",
  },
  { id: "e-agent-end", source: "agent-1", target: "end-1", type: "smoothstep" },
];

export default function NewWorkflowPage() {
  const user = useUser();
  const router = useRouter();
  const [name, setName] = useState("New Workflow");
  const [saving, setSaving] = useState(false);

  const handleSave = useCallback(
    async (nodes: Node[], edges: Edge[]) => {
      setSaving(true);
      try {
        const token = await user?.getAuthJson();
        if (!token?.accessToken) return;
        const wf = await workflowsApi.create(
          {
            name,
            nodes: nodes as ReturnType<
              typeof workflowsApi.create
            > extends Promise<infer T>
              ? T extends { nodes: infer N }
                ? N
                : never
              : never,
            edges: edges as ReturnType<
              typeof workflowsApi.create
            > extends Promise<infer T>
              ? T extends { edges: infer E }
                ? E
                : never
              : never,
          } as Parameters<typeof workflowsApi.create>[0],
          token.accessToken,
        );
        router.push(`/dashboard/workflows/${wf.id}/edit`);
      } catch (err: unknown) {
        alert(err instanceof Error ? err.message : "Save failed");
      } finally {
        setSaving(false);
      }
    },
    [name, user, router],
  );

  return (
    <div className="h-[calc(100vh-2rem)] -m-8 overflow-hidden">
      <WorkflowCanvas
        initialNodes={DEFAULT_NODES}
        initialEdges={DEFAULT_EDGES}
        workflowName={name}
        onNameChange={setName}
        onSave={handleSave}
        saving={saving}
      />
    </div>
  );
}
