import json

from fastapi import APIRouter

from scorecard_trust_layer.db import get_connection

router = APIRouter()


@router.get("/api/transcripts")
def list_transcripts():
    conn = get_connection()
    rows = conn.execute("SELECT id, raw_json, is_golden FROM transcripts ORDER BY id").fetchall()
    conn.close()
    return [
        {"id": r["id"], "transcript": json.loads(r["raw_json"]), "is_golden": bool(r["is_golden"])}
        for r in rows
    ]
