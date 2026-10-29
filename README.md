# Scorecard Trust Layer

A small demo built while applying for the Senior Product Engineer role at [Solidroad](https://www.solidroad.com). Solidroad scores support conversations against a rubric, flags gaps, and runs AI roleplay simulations to recertify agents. This project rebuilds that core loop — **transcript → LLM score → gap → roleplay simulation** — and adds the trust layer that loop depends on: **consistency**, **calibration**, and **drift** checks on the scorer itself.

## The three checks, in one sentence each

- **Consistency** — does the model agree with itself? Scores the same transcript multiple times and flags a dimension as low-confidence if the scores disagree.
- **Calibration** — is the model actually *right*? Compares its scores against a small set of tickets I hand-labeled.
- **Drift** — did a prompt or model change just make things worse? Re-runs the hand-labeled set after any change and flags a regression against the last run.

None of these improve the model — there's no fine-tuning here. They decide whether a score should be trusted automatically or routed to a human, and catch a regression before it ships, the same way a test suite doesn't make code better but tells you when a change broke something.

## Stack

- **Backend**: Python + FastAPI, `src/` package layout. LLM calls go through LangChain (`ChatOpenAI` + `.with_structured_output`) — used only as a model wrapper, not chains/agents, so every prompt is a single visible call in `scorer.py` / `simulation.py`.
- **Frontend**: Next.js + TypeScript.
- **Storage**: SQLite, no ORM.
- **Data**: 27 synthetic CRM/marketing-automation support tickets, spread across 4 topics (billing, deliverability, automation workflows, API/integrations). 16 are hand-scored as the golden set. No real customer data.

```
app.py                                    root entrypoint: `uvicorn app:app`
data/transcripts.json                     the 27 sample tickets
src/scorecard_trust_layer/
  main.py           FastAPI app, CORS, route registration
  config.py         env loading, model names, thresholds
  db.py             sqlite3 connection + schema
  rubric.py         the 4 scoring dimensions
  llm.py            LangChain model setup (primary + a cheaper model)
  scorer.py         one LLM call: score a transcript against the rubric
  simulation.py     generates a roleplay scenario for a flagged gap, runs it, re-scores it
  seed.py           loads data/transcripts.json into SQLite on first run
  trust/            consistency.py, calibration.py, drift.py
  routes/           FastAPI endpoints, one file per concern
frontend/
  app/page.tsx              pick a ticket, score it, see citations + confidence
  app/golden-set/page.tsx   hand-label the golden tickets
  app/reliability/page.tsx  calibration history, regression flags, MAE chart
  app/simulate/[gapId]/     the roleplay chat for a flagged gap
  app/dashboard/page.tsx    score and simulation history
```

## Running it

Backend (from the repo root):
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY
.venv/bin/uvicorn app:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_BASE=http://localhost:8000" > .env.local
npm run dev
```

Then open `http://localhost:3000`. The database seeds itself from `data/transcripts.json` on first run.

## Suggested walkthrough

1. **Score a ticket** on the home page (e.g. `t09`) and watch it get flagged as a gap.
2. **Label the golden set** — hand-score the 16 golden tickets. This is the one step that can't be faked.
3. **Run calibration** on the Reliability page — see how far the LLM's scores are from yours, per dimension.
4. **Run calibration again with the cheap-model toggle** — simulates swapping in a weaker model and shows the drift check catching the regression.
5. **Run a simulation** from a flagged gap — chat with the AI customer persona, finish it, see whether it recertifies.
6. **Check the dashboard** — score and simulation history across everything above.

## Known limitations

- The golden set's "ground truth" is my own hand labels, not a trained QA reviewer's.
- No automated test suite — manually verified during development.
- No auth, no multi-user, single SQLite file. Not built for production load.
