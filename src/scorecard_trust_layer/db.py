import sqlite3

from scorecard_trust_layer.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS transcripts (
    id TEXT PRIMARY KEY,
    raw_json TEXT NOT NULL,
    is_golden INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS golden_labels (
    transcript_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    human_score INTEGER NOT NULL,
    PRIMARY KEY (transcript_id, dimension)
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_id TEXT NOT NULL,
    scorer_version_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    llm_score REAL NOT NULL,
    stddev REAL NOT NULL,
    confidence TEXT NOT NULL,
    citation TEXT NOT NULL,
    rationale TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calibration_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scorer_version_id TEXT NOT NULL,
    model_used TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mae_json TEXT NOT NULL,
    agreement_rate REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS simulation_sessions (
    id TEXT PRIMARY KEY,
    gap_dimension TEXT NOT NULL,
    transcript_id TEXT NOT NULL,
    persona_prompt TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'in_progress',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
