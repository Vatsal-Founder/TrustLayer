from fastapi import APIRouter

from scorecard_trust_layer.db import get_connection

router = APIRouter()


@router.get("/api/dashboard")
def dashboard():
    conn = get_connection()
    score_rows = conn.execute(
        "SELECT dimension, llm_score, created_at FROM scores ORDER BY created_at"
    ).fetchall()
    sessions = conn.execute(
        "SELECT gap_dimension, status, created_at FROM simulation_sessions ORDER BY created_at"
    ).fetchall()
    conn.close()
    return {
        "score_history": [dict(r) for r in score_rows],
        "simulation_sessions": [dict(r) for r in sessions],
    }
