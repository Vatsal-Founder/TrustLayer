import statistics

from scorecard_trust_layer.config import CONSISTENCY_RUNS, CONSISTENCY_STDDEV_THRESHOLD
from scorecard_trust_layer.schemas import ScoreResult
from scorecard_trust_layer.scorer import score_transcript


def score_with_consistency(transcript: dict, use_cheap: bool = False) -> dict:
    """Scores the same transcript multiple times to measure how much the
    model agrees with itself, separately from whether it's actually right."""
    runs = [
        score_transcript(transcript, use_cheap=use_cheap, temperature=0.7)
        for _ in range(CONSISTENCY_RUNS)
    ]
    results = [r[0] for r in runs]
    scorer_version = runs[0][1]

    dimensions: dict[str, dict] = {}
    for key in ScoreResult.model_fields:
        scores = [getattr(r, key).score for r in results]
        mean_score = statistics.mean(scores)
        stddev = statistics.pstdev(scores)
        confidence = "low" if stddev > CONSISTENCY_STDDEV_THRESHOLD else "high"
        last = getattr(results[-1], key)
        dimensions[key] = {
            "score": round(mean_score, 2),
            "stddev": round(stddev, 2),
            "confidence": confidence,
            "citation": last.citation,
            "rationale": last.rationale,
        }

    return {"scorer_version_id": scorer_version, "dimensions": dimensions}
