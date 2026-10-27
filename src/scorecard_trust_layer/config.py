import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(REPO_ROOT / ".env")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PRIMARY_MODEL = os.environ.get("PRIMARY_MODEL", "gpt-4o")
CHEAP_MODEL = os.environ.get("CHEAP_MODEL", "gpt-4o-mini")

# How many times the scorer re-runs the same transcript to measure consistency.
CONSISTENCY_RUNS = 4
# Per-dimension stddev above this is flagged as "low confidence" / unstable.
CONSISTENCY_STDDEV_THRESHOLD = 0.8
# A calibration run whose MAE on a dimension rises by more than this vs. the
# previous run is flagged as a drift regression.
DRIFT_MAE_REGRESSION_THRESHOLD = 0.5
# A score at or below this on a high-confidence dimension counts as a gap.
GAP_THRESHOLD = 3

DB_PATH = REPO_ROOT / "trust_layer.db"
SAMPLE_DATA_PATH = REPO_ROOT / "data" / "transcripts.json"
