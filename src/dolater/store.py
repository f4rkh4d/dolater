"""sqlite layer. pure functions, db path injected so tests stay sane."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

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


class ListFull(Exception):
    """raised when trying to add a 4th item."""


class SlotEmpty(Exception):
    """raised when you done/drop a slot that isn't holding anything."""


class BadSlot(Exception):
    """slot number outside 1..3."""


@dataclass(frozen=True)
class Item:
    slot: int
    text: str
    added_at: str


@dataclass(frozen=True)
class LogEntry:
    action: str
    text: str
    timestamp: str


def default_db_path() -> Path:
    root = Path(os.environ.get("DOLATER_HOME", Path.home() / ".dolater"))
    return root / "state.db"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def list_items(conn: sqlite3.Connection) -> list[Item]:
    rows = conn.execute(
        "SELECT slot, text, added_at FROM items ORDER BY slot"
    ).fetchall()
    return [Item(r["slot"], r["text"], r["added_at"]) for r in rows]


def count_items(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]


def _next_free_slot(conn: sqlite3.Connection) -> int | None:
    taken = {r["slot"] for r in conn.execute("SELECT slot FROM items").fetchall()}
    for n in range(1, MAX_SLOTS + 1):
        if n not in taken:
            return n
    return None


def add_item(conn: sqlite3.Connection, text: str) -> Item:
    text = text.strip()
    if not text:
        raise ValueError("empty text")
    slot = _next_free_slot(conn)
    if slot is None:
        raise ListFull()
    added_at = _now()
    with conn:
        conn.execute(
            "INSERT INTO items (slot, text, added_at) VALUES (?,?,?)",
            (slot, text, added_at),
        )
    return Item(slot, text, added_at)


def _pop_slot(conn: sqlite3.Connection, slot: int, action: str) -> Item:
    if slot not in (1, 2, 3):
        raise BadSlot(slot)
    row = conn.execute(
        "SELECT slot, text, added_at FROM items WHERE slot = ?", (slot,)
    ).fetchone()
    if row is None:
        raise SlotEmpty(slot)
    item = Item(row["slot"], row["text"], row["added_at"])
    with conn:
        conn.execute("DELETE FROM items WHERE slot = ?", (slot,))
        conn.execute(
            "INSERT INTO log (action, text, timestamp) VALUES (?,?,?)",
            (action, item.text, _now()),
        )
    return item


def complete(conn: sqlite3.Connection, slot: int) -> Item:
    return _pop_slot(conn, slot, "done")


def drop(conn: sqlite3.Connection, slot: int) -> Item:
    return _pop_slot(conn, slot, "dropped")


def log_entries(conn: sqlite3.Connection, tail: int | None = None) -> list[LogEntry]:
    q = "SELECT action, text, timestamp FROM log ORDER BY id DESC"
    params: tuple = ()
    if tail is not None:
        q += " LIMIT ?"
        params = (int(tail),)
    rows = conn.execute(q, params).fetchall()
    return [LogEntry(r["action"], r["text"], r["timestamp"]) for r in rows]


def wipe(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute("DELETE FROM items")
        conn.execute("DELETE FROM log")


def iter_slots(items: list[Item]) -> Iterator[tuple[int, Item | None]]:
    """yield (slot, item-or-None) for slots 1..3. handy for rendering."""
    by_slot = {i.slot: i for i in items}
    for n in range(1, MAX_SLOTS + 1):
        yield n, by_slot.get(n)
