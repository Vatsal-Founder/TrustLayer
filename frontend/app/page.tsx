"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { api, DimensionKey, ScoreResponse, Transcript } from "@/lib/api";

const DIMENSION_LABELS: Record<DimensionKey, string> = {
  empathy: "Empathy",
  accuracy: "Accuracy",
  policy_adherence: "Policy adherence",
  clarity: "Clarity",
};

const AUDIO_DEMO_TICKET_ID = "t01";

function scoreBand(score: number): "score-high" | "score-mid" | "score-low" {
  if (score >= 4) return "score-high";
  if (score >= 3) return "score-mid";
  return "score-low";
}

export default function HomePage() {
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listTranscripts().then(setTranscripts).catch((e) => setError(String(e)));
  }, []);

  const selected = transcripts.find((t) => t.id === selectedId) ?? null;

  async function handleScore() {
    if (!selectedId) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.scoreTranscript(selectedId);
      setResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  function speak(transcript: Transcript) {
    const text = transcript.transcript.turns.map((t) => `${t.role}: ${t.message}`).join(". ");
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  }

  return (
    <div>
      <h1>Score a support ticket</h1>
      <p className="subtitle">
        Pick a ticket below. The scorer runs it 4 times and flags any dimension where it disagreed
        with itself as low-confidence, instead of trusting a single pass.
      </p>
      {error && <p className="error">{error}</p>}

      <div className="ticket-list">
        {transcripts.map((t) => (
          <button
            key={t.id}
            className={`ticket-item ${selectedId === t.id ? "selected" : ""}`}
            onClick={() => {
              setSelectedId(t.id);
              setResult(null);
            }}
          >
            <span>{t.id}</span>
            {t.is_golden && <span className="golden-badge">golden</span>}
          </button>
        ))}
      </div>

      {selected && (
        <div className="card">
          <div className="transcript-header">
            <h3>Transcript {selected.id}</h3>
            {selected.id === AUDIO_DEMO_TICKET_ID && (
              <button className="btn-secondary" onClick={() => speak(selected)}>
                Listen
              </button>
            )}
          </div>
          <div className="transcript">
            {selected.transcript.turns.map((turn, i) => (
              <p key={i} className={`turn turn-${turn.role}`}>
                <strong>{turn.role}:</strong> {turn.message}
              </p>
            ))}
          </div>
          <button className="btn" onClick={handleScore} disabled={loading}>
            {loading ? "Scoring (4 runs for consistency)..." : "Score this ticket"}
          </button>
        </div>
      )}

      {result && (
        <div className="card">
          <h3>Results</h3>
          {(Object.keys(result.dimensions) as DimensionKey[]).map((dim) => {
            const data = result.dimensions[dim];
            const isGap = result.gaps.includes(dim);
            return (
              <div key={dim} className="dim-row">
                <div className="dim-header">
                  <strong>{DIMENSION_LABELS[dim]}</strong>
                  <span className={`score-badge ${scoreBand(data.score)}`}>
                    {data.score.toFixed(1)}/5
                  </span>
                  {data.confidence === "low" && (
                    <span className="low-confidence-badge">
                      needs human review (stddev {data.stddev})
                    </span>
                  )}
                  {isGap && <span className="gap-badge">gap</span>}
                </div>
                <p className="citation">&ldquo;{data.citation}&rdquo;</p>
                <p className="rationale">{data.rationale}</p>
                {isGap && (
                  <Link
                    href={`/simulate/${dim}?transcript=${result.transcript_id}`}
                    className="btn-secondary"
                  >
                    Run a validation simulation
                  </Link>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
