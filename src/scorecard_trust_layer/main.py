from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scorecard_trust_layer.db import init_db
from scorecard_trust_layer.routes import calibration, dashboard, golden_set, score, simulation, transcripts
from scorecard_trust_layer.seed import seed_if_empty

app = FastAPI(title="Scorecard Trust Layer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
seed_if_empty()

app.include_router(score.router)
app.include_router(golden_set.router)
app.include_router(calibration.router)
app.include_router(simulation.router)
app.include_router(dashboard.router)
app.include_router(transcripts.router)
