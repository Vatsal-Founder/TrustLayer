"""Root entrypoint. Run with `uvicorn app:app --reload --port 8000` from the
repo root, or `python app.py` directly."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scorecard_trust_layer.main import app  # noqa: E402

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
