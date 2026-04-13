from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from forgetmail.config import CONFIG_DIR, ensure_config_dir

STATE_DB_PATH = CONFIG_DIR / "state.db"


class StateStore:
    def __init__(self, db_path: Path = STATE_DB_PATH):
        self.db_path = db_path

    def initialize(self) -> None:
        logging.debug("Store: initializing sqlite db at %s", self.db_path)
        ensure_config_dir()
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_messages (
                    message_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS config_cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS signal_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    score REAL NOT NULL,
                    notified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def unseen_ids(self, message_ids: list[str]) -> set[str]:
        if not message_ids:
            return set()

        logging.debug("Store: checking unseen ids for count=%s", len(message_ids))

        placeholders = ",".join("?" for _ in message_ids)
        query = f"SELECT message_id FROM seen_messages WHERE message_id IN ({placeholders})"
        with self._connect() as conn:
            rows = conn.execute(query, message_ids).fetchall()

        seen = {row[0] for row in rows}
        logging.debug("Store: seen ids count=%s", len(seen))
        return {message_id for message_id in message_ids if message_id not in seen}

    def mark_seen(self, rows: list[tuple[str, str]]) -> None:
        if not rows:
            return

        logging.debug("Store: marking seen rows=%s", len(rows))

        with self._connect() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO seen_messages (message_id, thread_id) VALUES (?, ?)",
                rows,
            )

    def record_signal_events(self, rows: list[tuple[str, str, str, str, str, float]]) -> None:
        if not rows:
            return

        logging.debug("Store: recording signal events rows=%s", len(rows))
        with self._connect() as conn:
            conn.executemany(
                (
                    "INSERT INTO signal_events "
                    "(message_id, thread_id, sender, subject, reason, score) "
                    "VALUES (?, ?, ?, ?, ?, ?)"
                ),
                rows,
            )

    def recent_signal_events(self, limit: int = 5) -> list[dict[str, str | float]]:
        with self._connect() as conn:
            raw_rows = conn.execute(
                (
                    "SELECT message_id, thread_id, sender, subject, reason, score, notified_at "
                    "FROM signal_events "
                    "ORDER BY id DESC LIMIT ?"
                ),
                (limit,),
            ).fetchall()

        rows: list[dict[str, str | float]] = []
        for raw in raw_rows:
            rows.append(
                {
                    "message_id": str(raw[0]),
                    "thread_id": str(raw[1]),
                    "sender": str(raw[2]),
                    "subject": str(raw[3]),
                    "reason": str(raw[4]),
                    "score": float(raw[5]),
                    "notified_at": str(raw[6]),
                }
            )
        return rows

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            seen_count = conn.execute("SELECT COUNT(*) FROM seen_messages").fetchone()[0]
            signal_count = conn.execute("SELECT COUNT(*) FROM signal_events").fetchone()[0]

        return {
            "seen_messages": int(seen_count),
            "signal_events": int(signal_count),
        }

    def _connect(self) -> sqlite3.Connection:
        logging.debug("Store: opening sqlite connection")
        return sqlite3.connect(self.db_path, timeout=30)
