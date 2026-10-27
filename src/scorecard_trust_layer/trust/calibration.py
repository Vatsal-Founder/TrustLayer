import json
import statistics

from scorecard_trust_layer.db import get_connection
from scorecard_trust_layer.scorer import score_transcript
from scorecard_trust_layer.trust.drift import check_drift


def run_calibration(use_cheap: bool = False) -> dict:
    """Scores every golden-set transcript and compares the LLM's scores to
    the human labels, per dimension. This is the check that catches the
    model being consistently wrong, not just noisy."""
    conn = get_connection()
    golden_rows = conn.execute(
        "SELECT id, raw_json FROM transcripts WHERE is_golden = 1"
    ).fetchall()

    per_dimension_errors: dict[str, list[float]] = {}
    per_dimension_exact: dict[str, list[bool]] = {}
    scorer_version = None

    for row in golden_rows:
        transcript = json.loads(row["raw_json"])
        labels = {
            r["dimension"]: r["human_score"]
            for r in conn.execute(
                "SELECT dimension, human_score FROM golden_labels WHERE transcript_id = ?",
                (row["id"],),
            ).fetchall()
        }
        if not labels:
            continue

        result, scorer_version = score_transcript(transcript, use_cheap=use_cheap, temperature=0.0)
        scores = result.model_dump()

        for dimension, human_score in labels.items():
            llm_score = scores[dimension]["score"]
            per_dimension_errors.setdefault(dimension, []).append(abs(llm_score - human_score))
            per_dimension_exact.setdefault(dimension, []).append(llm_score == human_score)

    mae_by_dimension = {
        dim: round(statistics.mean(errors), 3) for dim, errors in per_dimension_errors.items()
    }
    all_exact = [e for exacts in per_dimension_exact.values() for e in exacts]
    agreement_rate = round(sum(all_exact) / len(all_exact), 3) if all_exact else 0.0
    model_used = "cheap" if use_cheap else "primary"

    conn.execute(
        "INSERT INTO calibration_runs (scorer_version_id, model_used, mae_json, agreement_rate) "
        "VALUES (?, ?, ?, ?)",
        (scorer_version, model_used, json.dumps(mae_by_dimension), agreement_rate),
    )
    conn.commit()
    run_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.close()

    regressions = check_drift(run_id, mae_by_dimension)

    return {
        "run_id": run_id,
        "scorer_version_id": scorer_version,
        "model_used": model_used,
        "mae_by_dimension": mae_by_dimension,
        "agreement_rate": agreement_rate,
        "regressions": regressions,
    }
