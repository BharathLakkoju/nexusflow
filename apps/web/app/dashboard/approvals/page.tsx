"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/auth/hooks";
import { CheckCircle, XCircle, Clock, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { approvalsApi, type HumanApproval } from "@/lib/api";
import { DEMO_APPROVALS } from "@/lib/demo-data";
import { formatDate, truncate } from "@/lib/utils";

export default function ApprovalsPage() {
  const user = useUser();
  const [approvals, setApprovals] = useState<HumanApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);
  const [token, setToken] = useState("");

  const load = async () => {
    const t = await user?.getAuthJson();
    if (!t?.accessToken) return;
    setToken(t.accessToken);
    const list = await approvalsApi.list(t.accessToken);
    setApprovals(list.length > 0 ? list : DEMO_APPROVALS);
    setLoading(false);
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const handleAction = async (id: string, action: "approved" | "rejected") => {
    setActing(id);
    try {
      await approvalsApi.action(id, action, undefined, token);
      setApprovals((prev) => prev.filter((a) => a.id !== id));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActing(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-800 tracking-tighter text-brown-900">
          Human Approvals
        </h1>
        <p className="text-brown-500 text-sm mt-1">
          {approvals.length} pending approval{approvals.length !== 1 ? "s" : ""}
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="h-32 bg-brown-200 animate-pulse rounded-lg"
            />
          ))}
        </div>
      ) : approvals.length === 0 ? (
        <Card className="bg-brown-100 border-brown-200">
          <CardContent className="p-12 text-center">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <p className="text-brown-500">
              All caught up! No pending approvals.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {approvals.map((approval) => (
            <Card
              key={approval.id}
              className="bg-brown-100 border-brown-200 border-l-4 border-l-yellow-500"
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="h-4 w-4 text-yellow-400" />
                      <Badge
                        variant="outline"
                        className="text-yellow-400 border-yellow-500/40"
                      >
                        Pending
                      </Badge>
                      <span className="text-xs text-brown-400">
                        {formatDate(approval.created_at)}
                      </span>
                    </div>
                    <p className="text-brown-900 font-medium mb-1">
                      {truncate(approval.message || "Review required", 100)}
                    </p>
                    {approval.execution_id && (
                      <p className="text-xs text-brown-500">
                        Execution:{" "}
                        <span className="font-mono">
                          {approval.execution_id.slice(0, 16)}…
                        </span>
                      </p>
                    )}
                    {approval.context != null && (
                      <pre className="text-xs text-brown-600 bg-brown-200/60 rounded p-2 mt-2 max-h-24 overflow-y-auto whitespace-pre-wrap">
                        {typeof approval.context === "string"
                          ? approval.context
                          : JSON.stringify(approval.context as object, null, 2)}
                      </pre>
                    )}
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <Button
                      size="sm"
                      onClick={() => handleAction(approval.id, "approved")}
                      disabled={acting === approval.id}
                      className="bg-green-700 hover:bg-green-600 gap-1"
                    >
                      {acting === approval.id ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <CheckCircle className="h-3.5 w-3.5" />
                      )}
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleAction(approval.id, "rejected")}
                      disabled={acting === approval.id}
                      variant="ghost"
                      className="text-red-400 hover:text-red-300 hover:bg-red-900/20 gap-1"
                    >
                      <XCircle className="h-3.5 w-3.5" />
                      Reject
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
