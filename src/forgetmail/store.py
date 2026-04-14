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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS classification_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    important INTEGER NOT NULL,
                    score REAL NOT NULL,
                    reason TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    classified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS watch_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context TEXT NOT NULL,
                    boost REAL NOT NULL DEFAULT 0.20,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS watch_rule_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id INTEGER NOT NULL,
                    message_id TEXT NOT NULL,
                    context TEXT NOT NULL,
                    applied_boost REAL NOT NULL,
                    matched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(rule_id) REFERENCES watch_rules(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS muted_threads (
                    thread_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    muted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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

    def record_classification_events(
        self,
        rows: list[tuple[str, str, str, str, int, float, str, str, str]],
    ) -> None:
        if not rows:
            return

        logging.debug("Store: recording classification events rows=%s", len(rows))
        with self._connect() as conn:
            conn.executemany(
                (
                    "INSERT INTO classification_events "
                    "(message_id, thread_id, sender, subject, important, score, reason, provider, model) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                rows,
            )

    def recent_classification_events(self, limit: int = 20) -> list[dict[str, str | float | int]]:
        with self._connect() as conn:
            raw_rows = conn.execute(
                (
                    "SELECT message_id, thread_id, sender, subject, important, score, reason, "
                    "provider, model, classified_at "
                    "FROM classification_events "
                    "ORDER BY id DESC LIMIT ?"
                ),
                (limit,),
            ).fetchall()

        rows: list[dict[str, str | float | int]] = []
        for raw in raw_rows:
            rows.append(
                {
                    "message_id": str(raw[0]),
                    "thread_id": str(raw[1]),
                    "sender": str(raw[2]),
                    "subject": str(raw[3]),
                    "important": int(raw[4]),
                    "score": float(raw[5]),
                    "reason": str(raw[6]),
                    "provider": str(raw[7]),
                    "model": str(raw[8]),
                    "classified_at": str(raw[9]),
                }
            )
        return rows

    def add_watch_rule(self, context: str, boost: float = 0.20) -> int:
        context_value = context.strip()
        if not context_value:
            raise ValueError("Watch rule context cannot be empty.")

        boost_value = max(0.0, min(1.0, float(boost)))
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO watch_rules (context, boost, is_active) VALUES (?, ?, 1)",
                (context_value, boost_value),
            )
            return int(cursor.lastrowid)

    def list_watch_rules(self, active_only: bool = False) -> list[dict[str, str | float | int]]:
        query = "SELECT id, context, boost, is_active, created_at FROM watch_rules"
        params: tuple[int, ...] = ()
        if active_only:
            query += " WHERE is_active = ?"
            params = (1,)
        query += " ORDER BY id DESC"

        with self._connect() as conn:
            raw_rows = conn.execute(query, params).fetchall()

        rows: list[dict[str, str | float | int]] = []
        for raw in raw_rows:
            rows.append(
                {
                    "id": int(raw[0]),
                    "context": str(raw[1]),
                    "boost": float(raw[2]),
                    "is_active": int(raw[3]),
                    "created_at": str(raw[4]),
                }
            )
        return rows

    def delete_watch_rule(self, rule_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM watch_rules WHERE id = ?", (rule_id,))
            return cursor.rowcount > 0

    def match_watch_rules(
        self,
        sender: str,
        subject: str,
        snippet: str,
    ) -> list[dict[str, str | float | int]]:
        sender_lower = sender.lower()
        subject_lower = subject.lower()
        snippet_lower = snippet.lower()

        matches: list[dict[str, str | float | int]] = []
        for rule in self.list_watch_rules(active_only=True):
            context = str(rule["context"]).lower()
            if not context:
                continue
            if context in sender_lower or context in subject_lower or context in snippet_lower:
                matches.append(rule)
        return matches

    def record_watch_rule_events(self, rows: list[tuple[int, str, str, float]]) -> None:
        if not rows:
            return

        with self._connect() as conn:
            conn.executemany(
                (
                    "INSERT INTO watch_rule_events "
                    "(rule_id, message_id, context, applied_boost) VALUES (?, ?, ?, ?)"
                ),
                rows,
            )

    def mute_thread(self, thread_id: str, source: str = "telegram_button") -> None:
        thread_value = thread_id.strip()
        if not thread_value:
            raise ValueError("thread_id cannot be empty.")

        with self._connect() as conn:
            conn.execute(
                (
                    "INSERT OR REPLACE INTO muted_threads (thread_id, source, muted_at) "
                    "VALUES (?, ?, CURRENT_TIMESTAMP)"
                ),
                (thread_value, source),
            )

    def muted_threads(self, thread_ids: list[str]) -> set[str]:
        if not thread_ids:
            return set()

        placeholders = ",".join("?" for _ in thread_ids)
        query = f"SELECT thread_id FROM muted_threads WHERE thread_id IN ({placeholders})"
        with self._connect() as conn:
            rows = conn.execute(query, thread_ids).fetchall()

        return {str(row[0]) for row in rows}

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
            classification_count = conn.execute("SELECT COUNT(*) FROM classification_events").fetchone()[0]
            watch_rule_count = conn.execute("SELECT COUNT(*) FROM watch_rules WHERE is_active = 1").fetchone()[0]
            watch_rule_event_count = conn.execute("SELECT COUNT(*) FROM watch_rule_events").fetchone()[0]
            muted_thread_count = conn.execute("SELECT COUNT(*) FROM muted_threads").fetchone()[0]

        return {
            "seen_messages": int(seen_count),
            "signal_events": int(signal_count),
            "classification_events": int(classification_count),
            "watch_rules": int(watch_rule_count),
            "watch_rule_events": int(watch_rule_event_count),
            "muted_threads": int(muted_thread_count),
        }

    def _connect(self) -> sqlite3.Connection:
        logging.debug("Store: opening sqlite connection")
        return sqlite3.connect(self.db_path, timeout=30)
