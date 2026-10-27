# Scorecard Trust Layer

A small demo built while applying for the Senior Product Engineer role at [Solidroad](https://www.solidroad.com). Solidroad scores customer support conversations against a rubric, flags gaps, and runs AI roleplay simulations to recertify agents — confirmed from their site and nine published customer case studies (Ryanair, Crypto.com, ActiveCampaign, and others).

Every one of those case studies reports a business metric (CSAT, AHT, NPS) that implicitly depends on the AI scorer being right. None of them show how that scoring is validated, monitored for drift, or gated when the model is uncertain. This project rebuilds the core loop — **transcript → LLM score → gap → roleplay simulation** — and wraps it in the trust layer that loop depends on but that nothing public shows: **consistency**, **calibration**, and **drift** checks.

## The three checks, in one sentence each

- **Consistency** — does the model agree with itself? Scores the same transcript multiple times and flags a dimension as low-confidence if the scores disagree.
- **Calibration** — is the model actually *right*, not just consistent? Compares its scores against a small set of tickets a human (me) hand-labeled.
- **Drift** — did a prompt or model change just quietly make things worse? Re-runs the hand-labeled set after any change and flags a regression against the last known-good run.

None of these improve the model itself — there's no fine-tuning here. They decide whether a given score should be trusted automatically or routed to a human, and they catch a regression before it ships, the same way a test suite doesn't make your code better but tells you when a change broke something.

## Architecture

- **Backend**: Python + FastAPI, laid out as a standard `src/` package. All LLM calls go through LangChain (`ChatOpenAI` + `.with_structured_output`) — used narrowly as a model wrapper, not for chains or agents, so every prompt is a single visible call in `scorer.py` / `simulation.py`, not buried in framework internals.
- **Frontend**: Next.js + TypeScript, matching the stack named in Solidroad's own job post.
- **Storage**: SQLite, no ORM — plain `sqlite3` with a schema in `db.py`.
- **Data**: 27 synthetic support tickets (CRM/marketing-automation domain) I authored myself, formatted like a Zendesk/Intercom export, spread evenly across 4 topics (billing, deliverability, automation workflows, API/integrations). 16 are the "golden set" — tickets I hand-scored to use as the calibration answer key. No real customer data is used anywhere.

```
app.py                                    root entrypoint: `uvicorn app:app`
data/transcripts.json                     the 27 sample tickets
src/scorecard_trust_layer/
  main.py           FastAPI app, CORS, route registration
  config.py         env loading, model names, thresholds
  db.py             sqlite3 connection + schema
  rubric.py         the 4 scoring dimensions (empathy, accuracy, policy adherence, clarity)
  llm.py            LangChain model setup (primary + a cheaper model)
  scorer.py         one LLM call: score a transcript against the rubric
  simulation.py     generates a roleplay scenario for a flagged gap, runs the chat, re-scores it
  seed.py           loads data/transcripts.json into SQLite on first run
  trust/            the three checks, grouped together:
    consistency.py    runs the scorer N times on one transcript, measures agreement with itself
    calibration.py    runs the scorer against the golden set, measures error vs. human labels
    drift.py          diffs a calibration run against the previous one, flags regressions
  routes/           FastAPI endpoints, one file per concern
frontend/
  app/page.tsx              pick a ticket, score it, see citations + confidence
  app/golden-set/page.tsx   hand-label the golden tickets
  app/reliability/page.tsx  calibration history, regression flags, the MAE chart
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

1. **Score a ticket** on the home page — one that has an obvious flaw (e.g. `t09`, a dismissive deliverability reply) and watch it get flagged as a gap.
2. **Label the golden set** — go hand-score the 16 golden tickets. This is the one step that can't be faked; it's your own judgment becoming the answer key.
3. **Run calibration** on the Reliability page — see how far the LLM's scores are from yours, per dimension.
4. **Run calibration again with the cheap-model toggle** — this deliberately swaps in a weaker model to simulate a real-world mistake (swapping models to save cost) and shows the drift check catching the regression.
5. **Run a simulation** from a flagged gap — chat with the generated AI customer persona, finish it, and see whether it would recertify.
6. **Check the dashboard** — score and simulation history across everything you just did.

## Known limitations (stated honestly, not hidden)

- The golden set's "ground truth" is my own hand labels, not a trained QA reviewer's. Calibration is only as good as that answer key — in a real company this would come from a senior QA lead's judgment, not one engineer.
- No automated test suite. This is a manually-run demo project, verified by hand during development.
- No auth, no multi-user support, single SQLite file. Not built for production load.

## What I'd build next (not built, just scoped)

Solidroad's own coaching dashboard already shows whether a gap affects one agent or the whole team — a simple aggregate. The next step I'd take is **root-cause clustering**: instead of counting *how many* agents fail a dimension, cluster the *content* of the failures (via embeddings) to find whether a gap is actually a training problem (one agent, many ticket types) or a systemic one (many agents, one ticket type) — which usually means a policy or knowledge-base gap, not a coaching gap. That's a materially different fix, and surfacing it is a bigger win for the buyer persona in Solidroad's own case studies (a quality program lead reporting to leadership) than another per-agent score.
