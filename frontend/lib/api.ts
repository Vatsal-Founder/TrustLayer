const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}: ${text}`);
  }
  return res.json();
}

export type DimensionKey = "empathy" | "accuracy" | "policy_adherence" | "clarity";

export interface TranscriptTurn {
  role: "customer" | "agent";
  message: string;
}

export interface Transcript {
  id: string;
  transcript: { turns: TranscriptTurn[] };
  is_golden: boolean;
}

export interface DimensionResult {
  score: number;
  stddev: number;
  confidence: "high" | "low";
  citation: string;
  rationale: string;
}

export interface ScoreResponse {
  transcript_id: string;
  scorer_version_id: string;
  dimensions: Record<DimensionKey, DimensionResult>;
  gaps: DimensionKey[];
}

export interface GoldenSetEntry {
  id: string;
  transcript: { turns: TranscriptTurn[] };
  labels: Partial<Record<DimensionKey, number>>;
}

export interface CalibrationRun {
  run_id: number;
  scorer_version_id: string;
  model_used: string;
  timestamp: string;
  mae_by_dimension: Record<string, number>;
  agreement_rate: number;
}

export interface Regression {
  dimension: string;
  before_mae: number;
  after_mae: number;
  delta: number;
}

export interface CalibrationRunResponse extends CalibrationRun {
  regressions: Regression[];
}

export interface DashboardData {
  score_history: { dimension: string; llm_score: number; created_at: string }[];
  simulation_sessions: { gap_dimension: string; status: string; created_at: string }[];
}

export const api = {
  listTranscripts: () => request<Transcript[]>("/api/transcripts"),

  scoreTranscript: (transcript_id: string) =>
    request<ScoreResponse>("/api/score", {
      method: "POST",
      body: JSON.stringify({ transcript_id }),
    }),

  listGoldenSet: () => request<GoldenSetEntry[]>("/api/golden-set"),

  labelTranscript: (transcriptId: string, dimension: DimensionKey, human_score: number) =>
    request<{ ok: boolean }>(`/api/golden-set/${transcriptId}/label`, {
      method: "POST",
      body: JSON.stringify({ dimension, human_score }),
    }),

  runCalibration: (use_cheap_model: boolean) =>
    request<CalibrationRunResponse>("/api/calibration/run", {
      method: "POST",
      body: JSON.stringify({ use_cheap_model }),
    }),

  calibrationHistory: () => request<CalibrationRun[]>("/api/calibration/history"),

  startSimulation: (transcript_id: string, gap_dimension: DimensionKey) =>
    request<{ session_id: string; opening_message: string }>("/api/simulation/start", {
      method: "POST",
      body: JSON.stringify({ transcript_id, gap_dimension }),
    }),

  sendSimulationTurn: (session_id: string, message: string) =>
    request<{ customer_reply: string }>("/api/simulation/turn", {
      method: "POST",
      body: JSON.stringify({ session_id, message }),
    }),

  finishSimulation: (session_id: string) =>
    request<{ status: string; dimension: string; score: number }>("/api/simulation/finish", {
      method: "POST",
      body: JSON.stringify({ session_id }),
    }),

  dashboard: () => request<DashboardData>("/api/dashboard"),
};
