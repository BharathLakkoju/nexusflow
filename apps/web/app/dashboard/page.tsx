"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/auth/hooks";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  GitBranch,
  Bot,
  Zap,
  DollarSign,
  TrendingUp,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { analyticsApi, type AnalyticsDashboard } from "@/lib/api";
import { formatCost, formatTokens } from "@/lib/utils";

export default function DashboardPage() {
  const user = useUser();
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const token = await user?.getAuthJson();
        if (!token?.accessToken) return;
        const dash = await analyticsApi.dashboard(30, token.accessToken);
        setData(dash);
      } catch {
        // Ignore — user may not have an org yet
      } finally {
        setLoading(false);
      }
    };
    if (user) load();
  }, [user]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-800 animate-pulse rounded" />
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-32 bg-slate-800 animate-pulse rounded-lg"
            />
          ))}
        </div>
      </div>
    );
  }

  const successRate =
    data && data.total_executions > 0
      ? Math.round((data.successful_executions / data.total_executions) * 100)
      : 0;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white">Overview</h1>
        <p className="text-slate-400 text-sm mt-1">
          Last 30 days · {user?.displayName ?? ""}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: "Total Executions",
            value: data?.total_executions ?? 0,
            icon: Zap,
            color: "text-purple-400",
            sub: `${successRate}% success rate`,
          },
          {
            label: "Active Workflows",
            value: data?.active_workflows ?? 0,
            icon: GitBranch,
            color: "text-blue-400",
            sub: "running",
          },
          {
            label: "Tokens Used",
            value: formatTokens(data?.total_tokens ?? 0),
            icon: Bot,
            color: "text-green-400",
            sub: "total",
          },
          {
            label: "Total Cost",
            value: formatCost(data?.total_cost ?? 0),
            icon: DollarSign,
            color: "text-yellow-400",
            sub: "USD",
          },
        ].map((stat) => (
          <Card key={stat.label} className="bg-slate-900 border-slate-800">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm text-slate-400">{stat.label}</p>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-xs text-slate-500 mt-1">{stat.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Executions by day */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-base text-white">
              Executions Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={data?.executions_by_day ?? []}>
                <defs>
                  <linearGradient id="exGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                    borderRadius: 8,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#8b5cf6"
                  fill="url(#exGrad)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="successful"
                  stroke="#22c55e"
                  fill="none"
                  strokeWidth={1.5}
                  strokeDasharray="4 2"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Model usage */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-base text-white">
              Token Usage by Model
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={data?.token_usage_by_model ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="model"
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v) => v.split("/")[1] ?? v}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 11 }}
                  tickFormatter={(v) => formatTokens(v)}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                    borderRadius: 8,
                  }}
                  formatter={(v) => [formatTokens(Number(v)), "Tokens"]}
                />
                <Bar dataKey="tokens" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top workflows + Agent perf */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-base text-white">
              Top Workflows
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(data?.top_workflows ?? []).slice(0, 5).map((wf) => (
                <div
                  key={wf.workflow_id}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <GitBranch className="h-4 w-4 text-purple-400" />
                    <span className="text-sm text-white truncate max-w-[180px]">
                      {wf.name}
                    </span>
                  </div>
                  <Badge variant="secondary">{wf.executions} runs</Badge>
                </div>
              ))}
              {!data?.top_workflows?.length && (
                <p className="text-sm text-slate-500 text-center py-4">
                  No executions yet
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-base text-white">
              Agent Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(data?.agent_performance ?? []).map((a) => (
                <div key={a.agent_type} className="flex items-center gap-3">
                  <Bot className="h-4 w-4 text-slate-400 shrink-0" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-white capitalize">
                        {a.agent_type}
                      </span>
                      <span className="text-slate-400">{a.success_rate}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-800 rounded-full">
                      <div
                        className="h-full bg-purple-500 rounded-full transition-all"
                        style={{ width: `${a.success_rate}%` }}
                      />
                    </div>
                  </div>
                  {a.success_rate >= 80 ? (
                    <CheckCircle className="h-4 w-4 text-green-400" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-400" />
                  )}
                </div>
              ))}
              {!data?.agent_performance?.length && (
                <p className="text-sm text-slate-500 text-center py-4">
                  No agent data yet
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
