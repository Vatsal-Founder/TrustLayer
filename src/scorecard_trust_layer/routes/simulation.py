from fastapi import APIRouter

from scorecard_trust_layer.schemas import (
    SimulationFinishRequest,
    SimulationStartRequest,
    SimulationTurnRequest,
)
from scorecard_trust_layer.simulation import finish_simulation, run_turn, start_simulation

router = APIRouter()


@router.post("/api/simulation/start")
def start(request: SimulationStartRequest):
    return start_simulation(request.transcript_id, request.gap_dimension)


@router.post("/api/simulation/turn")
def turn(request: SimulationTurnRequest):
    return run_turn(request.session_id, request.message)


@router.post("/api/simulation/finish")
def finish(request: SimulationFinishRequest):
    return finish_simulation(request.session_id)
