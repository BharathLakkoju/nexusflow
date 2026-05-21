"use client";

import { useEffect, useState } from "react";
import { useUser } from "@stackframe/stack";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { analyticsApi, type AnalyticsDashboard } from "@/lib/api";
import { formatCost, formatTokens } from "@/lib/utils";

const COLORS = [
  "#8b5cf6",
  "#3b82f6",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
];

export default function AnalyticsPage() {
  const user = useUser();
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      const t = await user?.getAuthJson();
      if (!t?.accessToken) return;
      try {
        const dash = await analyticsApi.dashboard(30, t.accessToken);
        setData(dash);
      } catch {}
      setLoading(false);
    };
    if (user) load();
  }, [user]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-32 bg-slate-800 animate-pulse rounded" />
        <div className="grid grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-64 bg-slate-800 animate-pulse rounded-lg"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-slate-400 text-sm mt-1">Last 30 days</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Executions over time */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-sm text-white">
              Executions Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data?.executions_by_day ?? []}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" tick={{ fill: "#64748b", fontSize: 10 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#8b5cf6"
                  fill="url(#g1)"
                  strokeWidth={2}
                  name="Total"
                />
                <Area
                  type="monotone"
                  dataKey="successful"
                  stroke="#22c55e"
                  fill="url(#g2)"
                  strokeWidth={2}
                  name="Successful"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Cost by day */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-sm text-white">Cost Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data?.cost_by_day ?? []}>
                <defs>
                  <linearGradient id="g3" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" tick={{ fill: "#64748b", fontSize: 10 }} />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v) => `$${v.toFixed(3)}`}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                  }}
                  formatter={(v) => [formatCost(Number(v)), "Cost"]}
                />
                <Area
                  type="monotone"
                  dataKey="cost"
                  stroke="#f59e0b"
                  fill="url(#g3)"
                  strokeWidth={2}
                  name="Cost"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Tokens by model */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-sm text-white">
              Token Usage by Model
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={data?.token_usage_by_model ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="model"
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v: string) => v.split("/")[1] ?? v}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v) => formatTokens(v)}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                  }}
                  formatter={(v: number) => [formatTokens(v), "Tokens"]}
                />
                <Bar dataKey="tokens" radius={[4, 4, 0, 0]}>
                  {(data?.token_usage_by_model ?? []).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Agent performance pie */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-sm text-white">
              Agent Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={data?.agent_performance ?? []}
                  dataKey="total_runs"
                  nameKey="agent_type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ agent_type, percent }) =>
                    `${agent_type} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {(data?.agent_performance ?? []).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
