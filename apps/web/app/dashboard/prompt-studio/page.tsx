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
  "meta-llama/llama-3.3-70b-instruct:free",
  "google/gemma-3-27b-it:free",
  "deepseek/deepseek-r1:free",
  "qwen/qwen3-235b-a22b:free",
  "mistralai/mistral-7b-instruct:free",
  "meta-llama/llama-3.1-8b-instruct:free",
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
  const [model, setModel] = useState("meta-llama/llama-3.3-70b-instruct:free");
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
        <h1 className="text-2xl font-800 tracking-tighter text-brown-900">
          Prompt Studio
        </h1>
        <p className="text-brown-500 text-sm mt-1">
          Test prompts with any model and optionally inject RAG context
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: editor */}
        <div className="space-y-4">
          {/* Model selector */}
          <div>
            <label className="text-sm text-brown-600 block mb-1.5">Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-brown-100 border border-brown-200 rounded-lg text-brown-900 text-sm h-10 px-3"
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
            <label className="text-sm text-brown-600 block mb-1.5">
              System Prompt
            </label>
            <Textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              rows={3}
              className="bg-brown-100 border-brown-200 text-brown-900 resize-none"
            />
          </div>

          {/* User prompt */}
          <div>
            <label className="text-sm text-brown-600 block mb-1.5">
              User Prompt
            </label>
            <Textarea
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              rows={5}
              placeholder="Enter your prompt here..."
              className="bg-brown-100 border-brown-200 text-brown-900 resize-none"
            />
          </div>

          {/* RAG toggle */}
          <div className="flex items-center gap-3 bg-brown-100 border border-brown-200 rounded-lg p-3">
            <FileSearch className="h-4 w-4 text-brown-600" />
            <div className="flex-1">
              <p className="text-sm text-brown-900">Inject RAG Context</p>
              <p className="text-xs text-brown-500">
                Search knowledge base and prepend results
              </p>
            </div>
            <button
              onClick={() => setUseRag((p) => !p)}
              className={`relative w-10 h-5 rounded-full transition-colors ${useRag ? "bg-brown-700" : "bg-brown-200"}`}
            >
              <span
                className={`absolute top-0.5 left-0.5 h-4 w-4 bg-white rounded-full transition-transform ${useRag ? "translate-x-5" : ""}`}
              />
            </button>
          </div>

          {useRag && (
            <div>
              <label className="text-sm text-brown-600 block mb-1.5">
                RAG Search Query (optional)
              </label>
              <Input
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                placeholder="Leave empty to use user prompt as query"
                className="bg-brown-100 border-brown-200 text-brown-900"
              />
            </div>
          )}

          <Button
            onClick={run}
            disabled={running || !userPrompt.trim()}
            className="w-full bg-brown-700 hover:bg-brown-800 text-brown-50 gap-2"
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
          <label className="text-sm text-brown-600 block">Output</label>
          <div className="bg-brown-100 border border-brown-200 rounded-lg p-4 min-h-[400px]">
            {running && (
              <div className="flex items-center gap-2 text-brown-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Running…</span>
              </div>
            )}
            {result && (
              <div className="space-y-4">
                <div className="prose prose-sm prose-invert max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-brown-800 font-sans">
                    {result.output}
                  </pre>
                </div>
                <div className="border-t border-brown-200 pt-3 grid grid-cols-2 gap-2 text-xs text-brown-500">
                  <div>
                    Model:{" "}
                    <span className="text-brown-700">
                      {result.model.split("/")[1]}
                    </span>
                  </div>
                  <div>
                    Tokens:{" "}
                    <span className="text-brown-700">
                      {formatTokens(result.usage?.total_tokens ?? 0)}
                    </span>
                  </div>
                  <div>
                    Cost:{" "}
                    <span className="text-brown-700">
                      {formatCost(result.cost_estimate)}
                    </span>
                  </div>
                  <div>
                    Latency:{" "}
                    <span className="text-brown-700">
                      {result.latency_ms}ms
                    </span>
                  </div>
                  {result.rag_context_used && (
                    <div className="col-span-2 flex items-center gap-1 text-brown-600">
                      <FileSearch className="h-3 w-3" /> RAG context injected
                    </div>
                  )}
                </div>
              </div>
            )}
            {!running && !result && (
              <p className="text-brown-400 text-sm">
                Output will appear here after you run a prompt.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
