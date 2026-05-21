"use client";

import { useEffect, useRef, useState } from "react";
import { useUser } from "@stackframe/stack";
import {
  Upload,
  FileText,
  Trash2,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { documentsApi, type Document } from "@/lib/api";
import { formatDate, truncate } from "@/lib/utils";

const STATUS_CONFIG: Record<
  string,
  {
    icon: React.ReactNode;
    badge: "default" | "success" | "secondary" | "destructive" | "outline";
  }
> = {
  pending: { icon: <Clock className="h-3.5 w-3.5" />, badge: "secondary" },
  processing: {
    icon: <Loader2 className="h-3.5 w-3.5 animate-spin" />,
    badge: "default",
  },
  completed: {
    icon: <CheckCircle className="h-3.5 w-3.5" />,
    badge: "success",
  },
  failed: { icon: <XCircle className="h-3.5 w-3.5" />, badge: "destructive" },
};

export default function DocumentsPage() {
  const user = useUser();
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [token, setToken] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const load = async () => {
    const t = await user?.getAuthJson();
    if (!t?.accessToken) return;
    setToken(t.accessToken);
    const list = await documentsApi.list(t.accessToken);
    setDocs(list);
    setLoading(false);
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      // Upload via server-side route (keeps BLOB_READ_WRITE_TOKEN secret)
      const res = await fetch(
        `/api/upload?filename=${encodeURIComponent(file.name)}`,
        {
          method: "POST",
          body: file,
        },
      );
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.json();
      // Register with API
      const doc = await documentsApi.create(
        {
          name: file.name,
          file_url: blob.url,
          mime_type: file.type || "application/octet-stream",
          file_size: file.size,
        },
        token,
      );
      setDocs((prev) => [doc, ...prev]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this document?")) return;
    await documentsApi.delete(id, token);
    setDocs((prev) => prev.filter((d) => d.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Knowledge Base</h1>
          <p className="text-slate-400 text-sm mt-1">{docs.length} documents</p>
        </div>
        <div>
          <input
            type="file"
            ref={fileRef}
            onChange={handleUpload}
            className="hidden"
            accept=".pdf,.docx,.txt,.md,.html,.csv"
          />
          <Button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            className="bg-purple-600 hover:bg-purple-700 gap-2"
          >
            {uploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Upload className="h-4 w-4" />
            )}
            Upload Document
          </Button>
        </div>
      </div>

      <div className="text-xs text-slate-500 bg-slate-900/50 border border-slate-800 rounded-lg p-3">
        Supported: PDF, DOCX, TXT, MD, HTML, CSV · Files are stored on Vercel
        Blob and indexed for semantic search
      </div>

      {loading ? (
        <div className="grid gap-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-20 bg-slate-800 animate-pulse rounded-lg"
            />
          ))}
        </div>
      ) : docs.length === 0 ? (
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-12 text-center">
            <FileText className="h-12 w-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">
              No documents yet. Upload files to build your knowledge base.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {docs.map((doc) => {
            const cfg = STATUS_CONFIG[doc.status] ?? STATUS_CONFIG.pending;
            return (
              <Card key={doc.id} className="bg-slate-900 border-slate-800">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-blue-400 shrink-0" />
                      <div>
                        <p className="font-medium text-white">
                          {truncate(doc.name, 50)}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <div className="flex items-center gap-1">
                            {cfg.icon}
                            <Badge
                              variant={cfg.badge}
                              className="text-[10px] capitalize"
                            >
                              {doc.status}
                            </Badge>
                          </div>
                          {doc.chunk_count !== undefined &&
                            doc.chunk_count > 0 && (
                              <span className="text-xs text-slate-500">
                                {doc.chunk_count} chunks
                              </span>
                            )}
                          <span className="text-xs text-slate-600">
                            {formatDate(doc.created_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
