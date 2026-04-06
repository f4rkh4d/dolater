"""sqlite layer. schema only for now — crud comes next."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

MAX_SLOTS = 3

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    slot     INTEGER NOT NULL UNIQUE CHECK(slot BETWEEN 1 AND 3),
    text     TEXT    NOT NULL,
    added_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    action    TEXT NOT NULL CHECK(action IN ('done','dropped')),
    text      TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
"""


def default_db_path() -> Path:
    root = Path(os.environ.get("DOLATER_HOME", Path.home() / ".dolater"))
    return root / "state.db"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
