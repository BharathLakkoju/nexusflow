"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/auth/hooks";
import { Zap, Send, Loader2, FileSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { promptStudioApi } from "@/lib/api";
import { formatCost, formatTokens } from "@/lib/utils";

const MODELS = [
  "openai/gpt-4o-mini",
  "openai/gpt-4o",
  "anthropic/claude-3.5-sonnet",
  "anthropic/claude-3-haiku",
  "google/gemini-2.0-flash",
  "meta-llama/llama-3.1-8b-instruct",
];

interface RunResult {
  output: string;
  model: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  cost_estimate: number;
  rag_context_used: boolean;
  latency_ms: number;
}

export default function PromptStudioPage() {
  const user = useUser();
  const [model, setModel] = useState("openai/gpt-4o-mini");
  const [systemPrompt, setSystemPrompt] = useState(
    "You are a helpful AI assistant.",
  );
  const [userPrompt, setUserPrompt] = useState("");
  const [useRag, setUseRag] = useState(false);
  const [ragQuery, setRagQuery] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [token, setToken] = useState("");

  useEffect(() => {
    user?.getAuthJson().then((t) => {
      if (t?.accessToken) setToken(t.accessToken);
    });
  }, [user]);

  const run = async () => {
    if (!userPrompt.trim()) return;
    setRunning(true);
    setResult(null);
    try {
      const res = await promptStudioApi.run(
        {
          model,
          system_prompt: systemPrompt,
          user_prompt: userPrompt,
          use_rag: useRag,
          rag_query: useRag ? ragQuery || userPrompt : undefined,
        },
        token,
      );
      setResult(res as RunResult);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Run failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Prompt Studio</h1>
        <p className="text-slate-400 text-sm mt-1">
          Test prompts with any model and optionally inject RAG context
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: editor */}
        <div className="space-y-4">
          {/* Model selector */}
          <div>
            <label className="text-sm text-slate-400 block mb-1.5">Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg text-white text-sm h-10 px-3"
            >
              {MODELS.map((m) => (
                <option key={m} value={m}>
                  {m.split("/")[1]}
                </option>
              ))}
            </select>
          </div>

          {/* System prompt */}
          <div>
            <label className="text-sm text-slate-400 block mb-1.5">
              System Prompt
            </label>
            <Textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              rows={3}
              className="bg-slate-900 border-slate-700 text-white resize-none"
            />
          </div>

          {/* User prompt */}
          <div>
            <label className="text-sm text-slate-400 block mb-1.5">
              User Prompt
            </label>
            <Textarea
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              rows={5}
              placeholder="Enter your prompt here..."
              className="bg-slate-900 border-slate-700 text-white resize-none"
            />
          </div>

          {/* RAG toggle */}
          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-lg p-3">
            <FileSearch className="h-4 w-4 text-cyan-400" />
            <div className="flex-1">
              <p className="text-sm text-white">Inject RAG Context</p>
              <p className="text-xs text-slate-500">
                Search knowledge base and prepend results
              </p>
            </div>
            <button
              onClick={() => setUseRag((p) => !p)}
              className={`relative w-10 h-5 rounded-full transition-colors ${useRag ? "bg-purple-600" : "bg-slate-700"}`}
            >
              <span
                className={`absolute top-0.5 left-0.5 h-4 w-4 bg-white rounded-full transition-transform ${useRag ? "translate-x-5" : ""}`}
              />
            </button>
          </div>

          {useRag && (
            <div>
              <label className="text-sm text-slate-400 block mb-1.5">
                RAG Search Query (optional)
              </label>
              <Input
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                placeholder="Leave empty to use user prompt as query"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
          )}

          <Button
            onClick={run}
            disabled={running || !userPrompt.trim()}
            className="w-full bg-purple-600 hover:bg-purple-700 gap-2"
          >
            {running ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            Run
          </Button>
        </div>

        {/* Right: output */}
        <div className="space-y-4">
          <label className="text-sm text-slate-400 block">Output</label>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 min-h-[400px]">
            {running && (
              <div className="flex items-center gap-2 text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Running…</span>
              </div>
            )}
            {result && (
              <div className="space-y-4">
                <div className="prose prose-sm prose-invert max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-slate-200 font-sans">
                    {result.output}
                  </pre>
                </div>
                <div className="border-t border-slate-800 pt-3 grid grid-cols-2 gap-2 text-xs text-slate-500">
                  <div>
                    Model:{" "}
                    <span className="text-slate-400">
                      {result.model.split("/")[1]}
                    </span>
                  </div>
                  <div>
                    Tokens:{" "}
                    <span className="text-slate-400">
                      {formatTokens(result.usage?.total_tokens ?? 0)}
                    </span>
                  </div>
                  <div>
                    Cost:{" "}
                    <span className="text-slate-400">
                      {formatCost(result.cost_estimate)}
                    </span>
                  </div>
                  <div>
                    Latency:{" "}
                    <span className="text-slate-400">
                      {result.latency_ms}ms
                    </span>
                  </div>
                  {result.rag_context_used && (
                    <div className="col-span-2 flex items-center gap-1 text-cyan-400">
                      <FileSearch className="h-3 w-3" /> RAG context injected
                    </div>
                  )}
                </div>
              </div>
            )}
            {!running && !result && (
              <p className="text-slate-600 text-sm">
                Output will appear here after you run a prompt.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
