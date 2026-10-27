import json

from scorecard_trust_layer.config import DRIFT_MAE_REGRESSION_THRESHOLD
from scorecard_trust_layer.db import get_connection


def check_drift(current_run_id: int, current_mae: dict[str, float]) -> list[dict]:
    """Compares a calibration run against the one immediately before it and
    flags any dimension whose error got meaningfully worse."""
    conn = get_connection()
    previous = conn.execute(
        "SELECT mae_json FROM calibration_runs WHERE id < ? ORDER BY id DESC LIMIT 1",
        (current_run_id,),
    ).fetchone()
    conn.close()

    if previous is None:
        return []

    previous_mae = json.loads(previous["mae_json"])
    regressions = []
    for dimension, after in current_mae.items():
        before = previous_mae.get(dimension)
        if before is None:
            continue
        delta = round(after - before, 3)
        if delta > DRIFT_MAE_REGRESSION_THRESHOLD:
            regressions.append(
                {
                    "dimension": dimension,
                    "before_mae": before,
                    "after_mae": after,
                    "delta": delta,
                }
            )
    return regressions
