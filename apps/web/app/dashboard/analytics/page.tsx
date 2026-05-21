"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/auth/hooks";
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
import { DEMO_ANALYTICS } from "@/lib/demo-data";
import { isDemoMode } from "@/lib/demo-mode";
import { formatCost, formatTokens } from "@/lib/utils";

const COLORS = [
  "#9a6848",
  "#7d5038",
  "#6b4226",
  "#b8906a",
  "#d4b896",
  "#4a2c1c",
];

export default function AnalyticsPage() {
  const user = useUser();
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      if (isDemoMode()) {
        setData(DEMO_ANALYTICS);
        setLoading(false);
        return;
      }

      const t = await user?.getAuthJson();
      if (!t?.accessToken) {
        setLoading(false);
        return;
      }
      try {
        const dash = await analyticsApi.dashboard(30, t.accessToken);
        setData(dash);
      } catch {
        setData(DEMO_ANALYTICS);
      }
      setLoading(false);
    };
    if (user) load();
  }, [user]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-32 bg-brown-200 animate-pulse rounded" />
        <div className="grid grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-64 bg-brown-200 animate-pulse rounded-lg"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-800 tracking-tighter text-brown-900">
          Analytics
        </h1>
        <p className="text-brown-500 text-sm mt-1">Last 30 days</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Executions over time */}
        <Card className="bg-brown-100 border-brown-200">
          <CardHeader>
            <CardTitle className="text-sm text-brown-900">
              Executions Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data?.executions_by_day ?? []}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#9a6848" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#9a6848" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8d5c0" />
                <XAxis dataKey="day" tick={{ fill: "#9a6848", fontSize: 10 }} />
                <YAxis tick={{ fill: "#9a6848", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: "#faf6f1",
                    border: "1px solid #e8d5c0",
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#9a6848"
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
        <Card className="bg-brown-100 border-brown-200">
          <CardHeader>
            <CardTitle className="text-sm text-brown-900">
              Cost Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data?.cost_by_day ?? []}>
                <defs>
                  <linearGradient id="g3" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7d5038" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#7d5038" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8d5c0" />
                <XAxis dataKey="day" tick={{ fill: "#9a6848", fontSize: 10 }} />
                <YAxis
                  tick={{ fill: "#9a6848", fontSize: 10 }}
                  tickFormatter={(v) => `$${v.toFixed(3)}`}
                />
                <Tooltip
                  contentStyle={{
                    background: "#faf6f1",
                    border: "1px solid #e8d5c0",
                  }}
                  formatter={(v) => [formatCost(Number(v)), "Cost"]}
                />
                <Area
                  type="monotone"
                  dataKey="cost"
                  stroke="#7d5038"
                  fill="url(#g3)"
                  strokeWidth={2}
                  name="Cost"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Tokens by model */}
        <Card className="bg-brown-100 border-brown-200">
          <CardHeader>
            <CardTitle className="text-sm text-brown-900">
              Token Usage by Model
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={data?.token_usage_by_model ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8d5c0" />
                <XAxis
                  dataKey="model"
                  tick={{ fill: "#9a6848", fontSize: 10 }}
                  tickFormatter={(v: string) => v.split("/")[1] ?? v}
                />
                <YAxis
                  tick={{ fill: "#9a6848", fontSize: 10 }}
                  tickFormatter={(v) => formatTokens(v)}
                />
                <Tooltip
                  contentStyle={{
                    background: "#faf6f1",
                    border: "1px solid #e8d5c0",
                  }}
                  formatter={(v) => [formatTokens(Number(v)), "Tokens"]}
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
        <Card className="bg-brown-100 border-brown-200">
          <CardHeader>
            <CardTitle className="text-sm text-brown-900">
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
                  label={(props) => {
                    const agent_type = (
                      props as unknown as Record<string, unknown>
                    ).agent_type as string | undefined;
                    const percent = props.percent ?? 0;
                    return `${agent_type ?? ""} ${(percent * 100).toFixed(0)}%`;
                  }}
                >
                  {(data?.agent_performance ?? []).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#faf6f1",
                    border: "1px solid #e8d5c0",
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
