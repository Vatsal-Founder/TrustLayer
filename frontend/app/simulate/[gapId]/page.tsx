"use client";

import { Suspense, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";

import { api, DimensionKey } from "@/lib/api";

interface ChatTurn {
  role: "customer" | "agent";
  message: string;
}

export default function SimulatePage() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <SimulateContent />
    </Suspense>
  );
}

function SimulateContent() {
  const params = useParams<{ gapId: string }>();
  const searchParams = useSearchParams();
  const transcriptId = searchParams.get("transcript") ?? "";
  const gapDimension = params.gapId as DimensionKey;

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [result, setResult] = useState<{ status: string; dimension: string; score: number } | null>(
    null
  );
  const [loading, setLoading] = useState(false);

  async function handleStart() {
    setLoading(true);
    const res = await api.startSimulation(transcriptId, gapDimension);
    setSessionId(res.session_id);
    setTurns([{ role: "customer", message: res.opening_message }]);
    setLoading(false);
  }

  async function handleSend() {
    if (!sessionId || !input.trim()) return;
    const agentMessage = input;
    setInput("");
    setTurns((prev) => [...prev, { role: "agent", message: agentMessage }]);
    setLoading(true);
    const res = await api.sendSimulationTurn(sessionId, agentMessage);
    setTurns((prev) => [...prev, { role: "customer", message: res.customer_reply }]);
    setLoading(false);
  }

  async function handleFinish() {
    if (!sessionId) return;
    setLoading(true);
    const res = await api.finishSimulation(sessionId);
    setResult(res);
    setLoading(false);
  }

  return (
    <div>
      <h1>Validation simulation: {gapDimension}</h1>
      <p className="subtitle">
        This scenario is generated to specifically stress-test {gapDimension}. Reply as the
        agent; when you&apos;re done, finish the simulation to see if it would recertify.
      </p>

      {!sessionId && (
        <button className="btn" onClick={handleStart} disabled={loading}>
          {loading ? "Generating scenario..." : "Start simulation"}
        </button>
      )}

      {sessionId && (
        <div className="card">
          <div className="chat">
            {turns.map((t, i) => (
              <p key={i} className={`turn turn-${t.role}`}>
                <strong>{t.role === "customer" ? "Customer" : "You"}:</strong> {t.message}
              </p>
            ))}
          </div>
          {!result && (
            <div className="chat-input-row">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Reply as the agent..."
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
              />
              <button className="btn" onClick={handleSend} disabled={loading}>
                Send
              </button>
              <button
                className="btn-secondary"
                onClick={handleFinish}
                disabled={loading || turns.length < 2}
              >
                Finish &amp; score
              </button>
            </div>
          )}
          {result && (
            <div className={`result-banner ${result.status}`}>
              {result.status === "certified"
                ? `Certified: scored ${result.score}/5 on ${result.dimension}.`
                : `Needs another attempt: scored ${result.score}/5 on ${result.dimension}.`}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
