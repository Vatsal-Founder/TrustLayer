"use client";

import { useEffect, useState } from "react";

import { api, DimensionKey, GoldenSetEntry } from "@/lib/api";

const DIMENSIONS: DimensionKey[] = ["empathy", "accuracy", "policy_adherence", "clarity"];
const DIMENSION_LABELS: Record<DimensionKey, string> = {
  empathy: "Empathy",
  accuracy: "Accuracy",
  policy_adherence: "Policy adherence",
  clarity: "Clarity",
};

export default function GoldenSetPage() {
  const [entries, setEntries] = useState<GoldenSetEntry[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  async function refresh() {
    setEntries(await api.listGoldenSet());
  }

  useEffect(() => {
    refresh();
  }, []);

  const labeledCount = entries.filter((e) => Object.keys(e.labels).length === DIMENSIONS.length).length;
  const active = entries.find((e) => e.id === activeId) ?? null;

  async function handleLabel(transcriptId: string, dimension: DimensionKey, score: number) {
    await api.labelTranscript(transcriptId, dimension, score);
    await refresh();
  }

  return (
    <div>
      <h1>Golden set</h1>
      <p className="subtitle">
        Hand-score each of these {entries.length} tickets yourself, on the same 1-5 rubric. This
        becomes the answer key the calibration check compares the LLM against.{" "}
        {labeledCount}/{entries.length} fully labeled.
      </p>

      <div className="ticket-list">
        {entries.map((e) => {
          const done = Object.keys(e.labels).length === DIMENSIONS.length;
          return (
            <button
              key={e.id}
              className={`ticket-item ${activeId === e.id ? "selected" : ""} ${done ? "done" : ""}`}
              onClick={() => setActiveId(e.id)}
            >
              {e.id} {done && "(done)"}
            </button>
          );
        })}
      </div>

      {active && (
        <div className="card">
          <div className="transcript">
            {active.transcript.turns.map((turn, i) => (
              <p key={i} className={`turn turn-${turn.role}`}>
                <strong>{turn.role}:</strong> {turn.message}
              </p>
            ))}
          </div>
          {DIMENSIONS.map((dim) => (
            <div key={dim} className="label-row">
              <span>{DIMENSION_LABELS[dim]}</span>
              <div className="score-buttons">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    className={`score-btn ${active.labels[dim] === n ? "active" : ""}`}
                    onClick={() => handleLabel(active.id, dim, n)}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
