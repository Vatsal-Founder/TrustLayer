"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api, CalibrationRun, CalibrationRunResponse } from "@/lib/api";

const DIM_COLORS: Record<string, string> = {
  empathy: "#2563eb",
  accuracy: "#16a34a",
  policy_adherence: "#9333ea",
  clarity: "#dc2626",
};

export default function ReliabilityPage() {
  const [history, setHistory] = useState<CalibrationRun[]>([]);
  const [latest, setLatest] = useState<CalibrationRunResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setHistory(await api.calibrationHistory());
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleRun(useCheap: boolean) {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runCalibration(useCheap);
      setLatest(res);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  const chartData = history.map((h) => ({
    run: `#${h.run_id} (${h.model_used})`,
    ...h.mae_by_dimension,
  }));

  return (
    <div>
      <h1>Scorer reliability</h1>
      <p className="subtitle">
        Runs the scorer against every hand-labeled golden-set ticket and measures how far off it
        is from your own scores (mean absolute error, lower is better), per rubric dimension.
      </p>

      <div className="button-row">
        <button className="btn" onClick={() => handleRun(false)} disabled={loading}>
          {loading ? "Running..." : "Run calibration (primary model)"}
        </button>
        <button className="btn-secondary" onClick={() => handleRun(true)} disabled={loading}>
          Run calibration (cheap model, demo regression)
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      {latest && latest.regressions.length > 0 && (
        <div className="card regression-card">
          <h3>Regression detected</h3>
          {latest.regressions.map((r) => (
            <p key={r.dimension}>
              <strong>{r.dimension}</strong>: MAE went from {r.before_mae} to {r.after_mae} (+
              {r.delta}). Do not ship this change.
            </p>
          ))}
        </div>
      )}
      {latest && latest.regressions.length === 0 && (
        <div className="card">
          <p>No regression vs. the previous run. Agreement rate: {(latest.agreement_rate * 100).toFixed(0)}%.</p>
        </div>
      )}

      {history.length > 0 && (
        <div className="card chart-card">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="run" />
              <YAxis label={{ value: "MAE", angle: -90, position: "insideLeft" }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="empathy" stroke={DIM_COLORS.empathy} />
              <Line type="monotone" dataKey="accuracy" stroke={DIM_COLORS.accuracy} />
              <Line type="monotone" dataKey="policy_adherence" stroke={DIM_COLORS.policy_adherence} />
              <Line type="monotone" dataKey="clarity" stroke={DIM_COLORS.clarity} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <table className="history-table">
        <thead>
          <tr>
            <th>Run</th>
            <th>Model</th>
            <th>Agreement</th>
            <th>MAE by dimension</th>
          </tr>
        </thead>
        <tbody>
          {history.map((h) => (
            <tr key={h.run_id}>
              <td>#{h.run_id}</td>
              <td>{h.model_used}</td>
              <td>{(h.agreement_rate * 100).toFixed(0)}%</td>
              <td>
                {Object.entries(h.mae_by_dimension)
                  .map(([d, v]) => `${d}: ${v}`)
                  .join(", ")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
