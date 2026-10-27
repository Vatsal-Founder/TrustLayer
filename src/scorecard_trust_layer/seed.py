import json

from scorecard_trust_layer.config import SAMPLE_DATA_PATH
from scorecard_trust_layer.db import get_connection


def seed_if_empty() -> None:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) AS c FROM transcripts").fetchone()["c"]
    if count == 0:
        with open(SAMPLE_DATA_PATH) as f:
            tickets = json.load(f)
        for ticket in tickets:
            conn.execute(
                "INSERT INTO transcripts (id, raw_json, is_golden) VALUES (?, ?, ?)",
                (
                    ticket["id"],
                    json.dumps({"turns": ticket["turns"]}),
                    1 if ticket.get("is_golden") else 0,
                ),
            )
        conn.commit()
    conn.close()
