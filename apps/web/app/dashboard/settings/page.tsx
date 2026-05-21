"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/auth/hooks";
import { Key, Plus, Trash2, Copy, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
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

export default function SettingsPage() {
  const user = useUser();
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState("");
  const [creating, setCreating] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [token, setToken] = useState("");

  const load = async () => {
    const t = await user?.getAuthJson();
    if (!t?.accessToken) return;
    setToken(t.accessToken);
    const list = await apiFetch<ApiKey[]>("/keys", t.accessToken);
    setKeys(list);
    setLoading(false);
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const handleCreate = async () => {
    if (!newKeyName.trim()) return;
    setCreating(true);
    try {
      const result = await apiFetch<{ key: ApiKey; plaintext_key: string }>(
        "/keys",
        token,
        { method: "POST", body: JSON.stringify({ name: newKeyName }) },
      );
      setKeys((prev) => [...prev, result.key]);
      setNewKey(result.plaintext_key);
      setNewKeyName("");
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Create failed");
    } finally {
      setCreating(false);
    }
  };

  const handleRevoke = async (id: string) => {
    if (!confirm("Revoke this API key?")) return;
    await apiFetch(`/keys/${id}`, token, { method: "DELETE" });
    setKeys((prev) => prev.filter((k) => k.id !== id));
  };

  const copy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 text-sm mt-1">
          Manage API keys and account preferences
        </p>
      </div>

      {/* Account */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-base text-white">Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Name</span>
            <span className="text-white">{user?.displayName ?? "—"}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Email</span>
            <span className="text-white">{user?.primaryEmail ?? "—"}</span>
          </div>
        </CardContent>
      </Card>

      {/* API Keys */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-base text-white flex items-center gap-2">
            <Key className="h-4 w-4" /> API Keys
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* New key banner */}
          {newKey && (
            <div className="bg-green-900/30 border border-green-700/50 rounded-lg p-3">
              <p className="text-xs text-green-400 mb-1.5 font-medium">
                Copy your key now — it won't be shown again!
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-xs text-green-300 font-mono bg-black/30 rounded px-2 py-1 truncate">
                  {newKey}
                </code>
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-green-400 shrink-0"
                  onClick={() => copy(newKey)}
                >
                  {copied ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Create form */}
          <div className="flex gap-2">
            <Input
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              placeholder="Key name (e.g. Production)"
              className="bg-slate-800 border-slate-700 text-white"
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
            <Button
              onClick={handleCreate}
              disabled={creating || !newKeyName.trim()}
              className="bg-purple-600 hover:bg-purple-700 gap-1 shrink-0"
            >
              {creating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Create
            </Button>
          </div>

          {/* Keys list */}
          {loading ? (
            <div className="h-20 bg-slate-800 animate-pulse rounded" />
          ) : keys.length === 0 ? (
            <p className="text-sm text-slate-500 text-center py-4">
              No API keys yet
            </p>
          ) : (
            <div className="space-y-2">
              {keys.map((k) => (
                <div
                  key={k.id}
                  className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0"
                >
                  <div>
                    <p className="text-sm text-white">{k.name}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <code className="text-xs text-slate-500 font-mono">
                        {k.prefix}…
                      </code>
                      <Badge
                        variant={k.is_active ? "success" : "secondary"}
                        className="text-[10px]"
                      >
                        {k.is_active ? "active" : "revoked"}
                      </Badge>
                      <span className="text-xs text-slate-600">
                        {formatDate(k.created_at)}
                      </span>
                    </div>
                  </div>
                  {k.is_active && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRevoke(k.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
