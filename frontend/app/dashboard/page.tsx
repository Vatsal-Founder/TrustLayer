"use client";

import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api, DashboardData } from "@/lib/api";

const DIMENSIONS: { key: string; label: string; color: string }[] = [
  { key: "empathy", label: "Empathy", color: "var(--chart-1)" },
  { key: "accuracy", label: "Accuracy", color: "var(--chart-2)" },
  { key: "policy_adherence", label: "Policy adherence", color: "var(--chart-3)" },
  { key: "clarity", label: "Clarity", color: "var(--chart-4)" },
];

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    api.dashboard().then(setData);
  }, []);

  if (!data) {
    return (
      <div>
        <h1>Dashboard</h1>
        <p className="subtitle">Loading...</p>
      </div>
    );
  }

  const chartData = data.score_history.map((s, i) => ({
    index: i + 1,
    [s.dimension]: s.llm_score,
  }));

  const certifiedCount = data.simulation_sessions.filter((s) => s.status === "certified").length;
  const certRate =
    data.simulation_sessions.length > 0
      ? Math.round((certifiedCount / data.simulation_sessions.length) * 100)
      : null;

  return (
    <div>
      <h1>Dashboard</h1>
      <p className="subtitle">Score and simulation history across everything run so far.</p>

      <div className="stat-grid">
        <div className="stat-tile">
          <div className="stat-value">{data.score_history.length}</div>
          <div className="stat-label">Scores recorded</div>
        </div>
        <div className="stat-tile">
          <div className="stat-value">{data.simulation_sessions.length}</div>
          <div className="stat-label">Simulations run</div>
        </div>
        <div className="stat-tile">
          <div className="stat-value">{certRate !== null ? `${certRate}%` : "—"}</div>
          <div className="stat-label">
            Certified ({certifiedCount}/{data.simulation_sessions.length})
          </div>
        </div>
      </div>

      <div className="card chart-card">
        <h3>Score history</h3>
        {chartData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis
                  dataKey="index"
                  stroke="var(--text-muted)"
                  fontSize={12}
                  label={{ value: "Score #", position: "insideBottom", offset: -5, fill: "var(--text-muted)" }}
                />
                <YAxis domain={[1, 5]} stroke="var(--text-muted)" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.82rem",
                  }}
                />
                {DIMENSIONS.map((d) => (
                  <Line
                    key={d.key}
                    type="monotone"
                    dataKey={d.key}
                    stroke={d.color}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    connectNulls
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {DIMENSIONS.map((d) => (
                <span key={d.key} className="chart-legend-item">
                  <span className="chart-legend-dot" style={{ background: d.color }} />
                  {d.label}
                </span>
              ))}
            </div>
          </>
        ) : (
          <p className="empty-state">No scores yet — score a ticket on the home page to see it here.</p>
        )}
      </div>

      <div className="card">
        <h3>Simulation sessions</h3>
        {data.simulation_sessions.length > 0 ? (
          <table className="history-table">
            <thead>
              <tr>
                <th>Gap dimension</th>
                <th>Status</th>
                <th>When</th>
              </tr>
            </thead>
            <tbody>
              {data.simulation_sessions.map((s, i) => (
                <tr key={i}>
                  <td>{s.gap_dimension}</td>
                  <td>
                    <span className={`status-badge ${s.status}`}>{s.status.replace("_", " ")}</span>
                  </td>
                  <td>{s.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="empty-state">No simulations run yet — start one from a flagged gap on the home page.</p>
        )}
      </div>
    </div>
  );
}
