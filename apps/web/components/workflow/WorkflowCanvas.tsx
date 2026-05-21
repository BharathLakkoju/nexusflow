"use client";

import { useCallback, useRef, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
  type Connection,
  type Node,
  type Edge,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Plus,
  Save,
  Play,
  Trash2,
  Loader2,
  Bot,
  Wrench,
  Brain,
  FileSearch,
  GitBranch,
  Zap,
  User,
  Webhook,
  Clock,
  Flag,
  PlayCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

// ---- Node type definitions ----
const NODE_TYPES_META = [
  {
    type: "start",
    label: "Start",
    icon: PlayCircle,
    color: "#22c55e",
    description: "Workflow entry point",
  },
  {
    type: "end",
    label: "End",
    icon: Flag,
    color: "#ef4444",
    description: "Workflow exit point",
  },
  {
    type: "agent",
    label: "Agent",
    icon: Bot,
    color: "#8b5cf6",
    description: "AI agent node",
  },
  {
    type: "tool",
    label: "Tool",
    icon: Wrench,
    color: "#3b82f6",
    description: "Execute a tool",
  },
  {
    type: "memory",
    label: "Memory",
    icon: Brain,
    color: "#f59e0b",
    description: "Store/retrieve memory",
  },
  {
    type: "rag",
    label: "RAG",
    icon: FileSearch,
    color: "#06b6d4",
    description: "Semantic document search",
  },
  {
    type: "conditional",
    label: "Conditional",
    icon: GitBranch,
    color: "#f97316",
    description: "Branch on condition",
  },
  {
    type: "human_approval",
    label: "Approval",
    icon: User,
    color: "#ec4899",
    description: "Require human sign-off",
  },
  {
    type: "webhook",
    label: "Webhook",
    icon: Webhook,
    color: "#6366f1",
    description: "HTTP trigger",
  },
  {
    type: "scheduler",
    label: "Scheduler",
    icon: Clock,
    color: "#84cc16",
    description: "Timed trigger",
  },
] as const;

// ---- Custom node component ----
function WorkflowNode({
  data,
  selected,
}: {
  data: Record<string, unknown>;
  selected: boolean;
}) {
  const meta = NODE_TYPES_META.find((m) => m.type === data.nodeType);
  const Icon = meta?.icon ?? Zap;
  const color = meta?.color ?? "#6366f1";

  return (
    <div
      className={`bg-slate-900 border-2 rounded-xl px-4 py-3 min-w-[140px] shadow-lg transition-all ${
        selected
          ? "border-purple-400 shadow-purple-500/20 shadow-lg"
          : "border-slate-700"
      }`}
      style={{ borderColor: selected ? undefined : color + "66" }}
    >
      <div className="flex items-center gap-2">
        <div
          className="h-6 w-6 rounded-md flex items-center justify-center"
          style={{ backgroundColor: color + "22" }}
        >
          <Icon className="h-3.5 w-3.5" style={{ color }} />
        </div>
        <div>
          <p className="text-xs font-semibold text-white">
            {String(data.label ?? meta?.label ?? "Node")}
          </p>
          {data.model && (
            <p className="text-[10px] text-slate-500">
              {String(data.model).split("/")[1]}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

const nodeTypes = { custom: WorkflowNode };

let nodeCounter = 0;

// ---- NodePalette ----
function NodePalette({ onAdd }: { onAdd: (type: string) => void }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 space-y-1 w-44">
      <p className="text-xs font-medium text-slate-400 mb-2 px-1">Add Node</p>
      {NODE_TYPES_META.map((m) => (
        <button
          key={m.type}
          onClick={() => onAdd(m.type)}
          className="flex items-center gap-2 w-full px-2 py-1.5 rounded-lg text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <m.icon className="h-3.5 w-3.5 shrink-0" style={{ color: m.color }} />
          {m.label}
        </button>
      ))}
    </div>
  );
}

// ---- NodeEditor ----
function NodeEditor({
  node,
  onChange,
  onClose,
}: {
  node: Node;
  onChange: (id: string, data: Record<string, unknown>) => void;
  onClose: () => void;
}) {
  const data = node.data as Record<string, unknown>;
  const meta = NODE_TYPES_META.find((m) => m.type === data.nodeType);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 w-64 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-white">
          {meta?.label ?? "Node"} Settings
        </p>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white text-xs"
        >
          ✕
        </button>
      </div>

      <div>
        <label className="text-xs text-slate-400 block mb-1">Label</label>
        <Input
          value={String(data.label ?? "")}
          onChange={(e) =>
            onChange(node.id, { ...data, label: e.target.value })
          }
          className="bg-slate-800 border-slate-700 text-white h-8 text-sm"
        />
      </div>

      {data.nodeType === "agent" && (
        <>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Model</label>
            <select
              value={String(data.model ?? "openai/gpt-4o-mini")}
              onChange={(e) =>
                onChange(node.id, { ...data, model: e.target.value })
              }
              className="w-full bg-slate-800 border border-slate-700 rounded-md text-white text-sm h-8 px-2"
            >
              <option value="openai/gpt-4o-mini">GPT-4o Mini</option>
              <option value="openai/gpt-4o">GPT-4o</option>
              <option value="anthropic/claude-3.5-sonnet">
                Claude 3.5 Sonnet
              </option>
              <option value="anthropic/claude-3-haiku">Claude 3 Haiku</option>
              <option value="google/gemini-2.0-flash">Gemini 2.0 Flash</option>
              <option value="meta-llama/llama-3.1-8b-instruct">
                Llama 3.1 8B
              </option>
            </select>
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">
              Prompt Template
            </label>
            <textarea
              value={String(data.prompt ?? "")}
              onChange={(e) =>
                onChange(node.id, { ...data, prompt: e.target.value })
              }
              placeholder="{{input}}"
              rows={3}
              className="w-full bg-slate-800 border border-slate-700 rounded-md text-white text-sm p-2 resize-none"
            />
            <p className="text-[10px] text-slate-500 mt-1">
              Use {"{{variable}}"} for context variables
            </p>
          </div>
        </>
      )}

      {data.nodeType === "tool" && (
        <div>
          <label className="text-xs text-slate-400 block mb-1">Tool</label>
          <select
            value={String(data.toolName ?? "web_search")}
            onChange={(e) =>
              onChange(node.id, { ...data, toolName: e.target.value })
            }
            className="w-full bg-slate-800 border border-slate-700 rounded-md text-white text-sm h-8 px-2"
          >
            <option value="web_search">Web Search</option>
            <option value="execute_python">Execute Python</option>
            <option value="http_request">HTTP Request</option>
            <option value="file_read">File Read</option>
          </select>
        </div>
      )}

      {data.nodeType === "conditional" && (
        <div>
          <label className="text-xs text-slate-400 block mb-1">Condition</label>
          <Input
            value={String(data.condition ?? "")}
            onChange={(e) =>
              onChange(node.id, { ...data, condition: e.target.value })
            }
            placeholder="{{output}} contains 'success'"
            className="bg-slate-800 border-slate-700 text-white h-8 text-sm"
          />
        </div>
      )}

      {data.nodeType === "human_approval" && (
        <div>
          <label className="text-xs text-slate-400 block mb-1">Message</label>
          <textarea
            value={String(data.message ?? "")}
            onChange={(e) =>
              onChange(node.id, { ...data, message: e.target.value })
            }
            placeholder="Please review the output..."
            rows={2}
            className="w-full bg-slate-800 border border-slate-700 rounded-md text-white text-sm p-2 resize-none"
          />
        </div>
      )}
    </div>
  );
}

// ---- Main WorkflowCanvas ----
interface WorkflowCanvasProps {
  initialNodes?: Node[];
  initialEdges?: Edge[];
  workflowName: string;
  onNameChange: (name: string) => void;
  onSave: (nodes: Node[], edges: Edge[]) => Promise<void>;
  onExecute?: () => void;
  saving: boolean;
}

export function WorkflowCanvas({
  initialNodes = [],
  initialEdges = [],
  workflowName,
  onNameChange,
  onSave,
  onExecute,
  saving,
}: WorkflowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [showPalette, setShowPalette] = useState(false);

  const onConnect = useCallback(
    (params: Connection) =>
      setEdges((eds) => addEdge({ ...params, type: "smoothstep" }, eds)),
    [setEdges],
  );

  const addNode = useCallback(
    (type: string) => {
      nodeCounter++;
      const meta = NODE_TYPES_META.find((m) => m.type === type);
      const newNode: Node = {
        id: `node-${nodeCounter}`,
        type: "custom",
        position: {
          x: 200 + (nodeCounter % 4) * 180,
          y: 100 + Math.floor(nodeCounter / 4) * 120,
        },
        data: {
          nodeType: type,
          label: meta?.label ?? type,
          model: type === "agent" ? "openai/gpt-4o-mini" : undefined,
          prompt: type === "agent" ? "{{input}}" : undefined,
          toolName: type === "tool" ? "web_search" : undefined,
        },
      };
      setNodes((nds) => [...nds, newNode]);
      setShowPalette(false);
    },
    [setNodes],
  );

  const updateNodeData = useCallback(
    (id: string, data: Record<string, unknown>) => {
      setNodes((nds) => nds.map((n) => (n.id === id ? { ...n, data } : n)));
      setSelectedNode((prev) => (prev?.id === id ? { ...prev, data } : prev));
    },
    [setNodes],
  );

  const deleteSelected = useCallback(() => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id));
      setEdges((eds) =>
        eds.filter(
          (e) => e.source !== selectedNode.id && e.target !== selectedNode.id,
        ),
      );
      setSelectedNode(null);
    }
  }, [selectedNode, setNodes, setEdges]);

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center gap-3 p-3 border-b border-slate-800 bg-slate-900/80 backdrop-blur shrink-0">
        <Input
          value={workflowName}
          onChange={(e) => onNameChange(e.target.value)}
          className="bg-slate-800 border-slate-700 text-white h-8 text-sm max-w-[240px]"
          placeholder="Workflow name..."
        />
        <div className="flex items-center gap-2 ml-auto">
          <div className="relative">
            <Button
              size="sm"
              variant="outline"
              className="border-slate-700 text-slate-300 gap-1"
              onClick={() => setShowPalette((p) => !p)}
            >
              <Plus className="h-4 w-4" /> Add Node
            </Button>
            {showPalette && (
              <div className="absolute top-full mt-2 left-0 z-50">
                <NodePalette onAdd={addNode} />
              </div>
            )}
          </div>

          {selectedNode && (
            <Button
              size="sm"
              variant="ghost"
              className="text-red-400 hover:text-red-300 gap-1"
              onClick={deleteSelected}
            >
              <Trash2 className="h-4 w-4" /> Delete
            </Button>
          )}

          <Button
            size="sm"
            onClick={() => onSave(nodes, edges)}
            disabled={saving}
            className="bg-purple-600 hover:bg-purple-700 gap-1"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Save
          </Button>

          {onExecute && (
            <Button
              size="sm"
              onClick={onExecute}
              className="bg-green-600 hover:bg-green-700 gap-1"
            >
              <Play className="h-4 w-4" /> Run
            </Button>
          )}
        </div>
      </div>

      {/* Canvas + Editor */}
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onNodeClick={(_, node) => setSelectedNode(node)}
            onPaneClick={() => setSelectedNode(null)}
            fitView
            className="bg-slate-950"
          >
            <Background
              variant={BackgroundVariant.Dots}
              gap={20}
              size={1}
              color="#1e293b"
            />
            <Controls className="fill-slate-700" />
            <MiniMap
              className="bg-slate-900 border border-slate-800"
              nodeColor="#8b5cf6"
            />
            <Panel position="top-left">
              <div className="flex items-center gap-2 text-xs text-slate-500 bg-slate-900/80 px-3 py-1.5 rounded-full border border-slate-800">
                <span>{nodes.length} nodes</span>
                <span>·</span>
                <span>{edges.length} edges</span>
              </div>
            </Panel>
          </ReactFlow>
        </div>

        {/* Node editor panel */}
        {selectedNode && (
          <div className="w-72 border-l border-slate-800 bg-slate-900/50 p-4 overflow-y-auto">
            <NodeEditor
              node={selectedNode}
              onChange={updateNodeData}
              onClose={() => setSelectedNode(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
