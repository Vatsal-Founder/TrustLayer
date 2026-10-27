import json

from fastapi import APIRouter, HTTPException

from scorecard_trust_layer.config import GAP_THRESHOLD
from scorecard_trust_layer.db import get_connection
from scorecard_trust_layer.schemas import ScoreRequest
from scorecard_trust_layer.trust.consistency import score_with_consistency

router = APIRouter()


@router.post("/api/score")
def score(request: ScoreRequest):
    conn = get_connection()
    row = conn.execute(
        "SELECT raw_json FROM transcripts WHERE id = ?", (request.transcript_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="transcript not found")
    transcript = json.loads(row["raw_json"])

    result = score_with_consistency(transcript)

    # A gap only auto-counts if the score is both low AND the scorer agreed
    # with itself across the repeated runs - a noisy low score gets routed
    # to human review instead of silently becoming a certified "gap".
    gaps = [
        dim
        for dim, data in result["dimensions"].items()
        if data["score"] <= GAP_THRESHOLD and data["confidence"] == "high"
    ]

    for dim, data in result["dimensions"].items():
        conn.execute(
            "INSERT INTO scores "
            "(transcript_id, scorer_version_id, dimension, llm_score, stddev, confidence, citation, rationale) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                request.transcript_id,
                result["scorer_version_id"],
                dim,
                data["score"],
                data["stddev"],
                data["confidence"],
                data["citation"],
                data["rationale"],
            ),
        )
    conn.commit()
    conn.close()

    return {
        "transcript_id": request.transcript_id,
        "scorer_version_id": result["scorer_version_id"],
        "dimensions": result["dimensions"],
        "gaps": gaps,
    }
