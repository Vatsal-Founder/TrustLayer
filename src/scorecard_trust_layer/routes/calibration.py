import json

from fastapi import APIRouter

from scorecard_trust_layer.db import get_connection
from scorecard_trust_layer.schemas import CalibrationRunRequest
from scorecard_trust_layer.trust.calibration import run_calibration

router = APIRouter()


@router.post("/api/calibration/run")
def run(request: CalibrationRunRequest):
    return run_calibration(use_cheap=request.use_cheap_model)


@router.get("/api/calibration/history")
def history():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, scorer_version_id, model_used, timestamp, mae_json, agreement_rate "
        "FROM calibration_runs ORDER BY id"
    ).fetchall()
    conn.close()
    return [
        {
            "run_id": r["id"],
            "scorer_version_id": r["scorer_version_id"],
            "model_used": r["model_used"],
            "timestamp": r["timestamp"],
            "mae_by_dimension": json.loads(r["mae_json"]),
            "agreement_rate": r["agreement_rate"],
        }
        for r in rows
    ]
