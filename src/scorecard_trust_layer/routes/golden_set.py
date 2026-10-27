import json

from fastapi import APIRouter

from scorecard_trust_layer.db import get_connection
from scorecard_trust_layer.schemas import LabelRequest

router = APIRouter()


@router.get("/api/golden-set")
def list_golden_set():
    conn = get_connection()
    rows = conn.execute("SELECT id, raw_json FROM transcripts WHERE is_golden = 1").fetchall()
    result = []
    for row in rows:
        labels = {
            r["dimension"]: r["human_score"]
            for r in conn.execute(
                "SELECT dimension, human_score FROM golden_labels WHERE transcript_id = ?",
                (row["id"],),
            ).fetchall()
        }
        result.append({"id": row["id"], "transcript": json.loads(row["raw_json"]), "labels": labels})
    conn.close()
    return result


@router.post("/api/golden-set/{transcript_id}/label")
def label_transcript(transcript_id: str, request: LabelRequest):
    conn = get_connection()
    conn.execute(
        "INSERT INTO golden_labels (transcript_id, dimension, human_score) VALUES (?, ?, ?) "
        "ON CONFLICT(transcript_id, dimension) DO UPDATE SET human_score = excluded.human_score",
        (transcript_id, request.dimension, request.human_score),
    )
    conn.commit()
    conn.close()
    return {"ok": True}
