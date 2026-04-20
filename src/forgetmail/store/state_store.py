from __future__ import annotations

import logging
import sqlite3
from email.utils import parseaddr
from pathlib import Path

from forgetmail.config import ensure_config_dir

from .constants import STATE_DB_PATH
from .mappers import (
    classification_event_row_to_dict,
    feedback_correction_row_to_dict,
    signal_event_row_to_dict,
    vip_sender_row_to_dict,
    watch_rule_row_to_dict,
)
from .schema import apply_schema


class StateStore:
    def __init__(self, db_path: Path = STATE_DB_PATH):
        self.db_path = db_path

    def initialize(self) -> None:
        logging.debug("Store: initializing sqlite db at %s", self.db_path)
        ensure_config_dir()
        with self._connect() as conn:
            apply_schema(conn)

    def get_cache_value(self, key: str) -> str | None:
        cache_key = key.strip()
        if not cache_key:
            return None

        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM config_cache WHERE key = ?",
                (cache_key,),
            ).fetchone()

        if row is None:
            return None
        return str(row[0])

    def set_cache_value(self, key: str, value: str) -> None:
        cache_key = key.strip()
        if not cache_key:
            raise ValueError("Cache key cannot be empty.")

        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO config_cache (key, value) VALUES (?, ?)",
                (cache_key, str(value)),
            )

    def delete_cache_value(self, key: str) -> None:
        cache_key = key.strip()
        if not cache_key:
            return

        with self._connect() as conn:
            conn.execute("DELETE FROM config_cache WHERE key = ?", (cache_key,))

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

        return [classification_event_row_to_dict(raw) for raw in raw_rows]

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

        return [watch_rule_row_to_dict(raw) for raw in raw_rows]

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

    def add_vip_sender(self, sender_email: str, display_name: str = "") -> bool:
        _display_name, parsed_email = parseaddr(sender_email)
        email_value = parsed_email.strip().lower()
        if not email_value:
            email_value = sender_email.strip().lower()
        display_value = display_name.strip()
        if not email_value:
            raise ValueError("sender_email cannot be empty.")

        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT OR REPLACE INTO vip_senders (sender_email, display_name) VALUES (?, ?)",
                (email_value, display_value),
            )
            return cursor.rowcount > 0

    def remove_vip_sender(self, sender_email: str) -> bool:
        _display_name, parsed_email = parseaddr(sender_email)
        email_value = parsed_email.strip().lower()
        if not email_value:
            email_value = sender_email.strip().lower()
        if not email_value:
            return False

        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM vip_senders WHERE sender_email = ?", (email_value,))
            return cursor.rowcount > 0

    def list_vip_senders(self) -> list[dict[str, str]]:
        with self._connect() as conn:
            raw_rows = conn.execute(
                "SELECT sender_email, display_name, created_at FROM vip_senders ORDER BY sender_email"
            ).fetchall()

        return [vip_sender_row_to_dict(raw) for raw in raw_rows]

    def vip_senders(self, sender_emails: list[str]) -> set[str]:
        if not sender_emails:
            return set()

        normalized: list[str] = []
        for item in sender_emails:
            _display_name, parsed_email = parseaddr(item)
            email_value = parsed_email.strip().lower()
            if not email_value:
                email_value = item.strip().lower()
            if email_value:
                normalized.append(email_value)
        if not normalized:
            return set()

        placeholders = ",".join("?" for _ in normalized)
        query = f"SELECT sender_email FROM vip_senders WHERE sender_email IN ({placeholders})"
        with self._connect() as conn:
            rows = conn.execute(query, normalized).fetchall()

        return {str(row[0]).lower() for row in rows}

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

    def mute_message(
        self,
        message_id: str,
        thread_id: str,
        source: str = "telegram_button",
    ) -> None:
        message_value = message_id.strip()
        thread_value = thread_id.strip()
        if not message_value or not thread_value:
            raise ValueError("message_id and thread_id cannot be empty.")

        with self._connect() as conn:
            conn.execute(
                (
                    "INSERT OR REPLACE INTO muted_messages "
                    "(message_id, thread_id, source, muted_at) "
                    "VALUES (?, ?, ?, CURRENT_TIMESTAMP)"
                ),
                (message_value, thread_value, source),
            )

    def unmute_thread(self, thread_id: str) -> bool:
        thread_value = thread_id.strip()
        if not thread_value:
            return False

        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM muted_threads WHERE thread_id = ?", (thread_value,))
            return cursor.rowcount > 0

    def unmute_message(self, message_id: str) -> bool:
        message_value = message_id.strip()
        if not message_value:
            return False

        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM muted_messages WHERE message_id = ?",
                (message_value,),
            )
            return cursor.rowcount > 0

    def muted_threads(self, thread_ids: list[str]) -> set[str]:
        if not thread_ids:
            return set()

        placeholders = ",".join("?" for _ in thread_ids)
        query = f"SELECT thread_id FROM muted_threads WHERE thread_id IN ({placeholders})"
        with self._connect() as conn:
            rows = conn.execute(query, thread_ids).fetchall()

        return {str(row[0]) for row in rows}

    def muted_messages(self, message_ids: list[str]) -> set[str]:
        if not message_ids:
            return set()

        placeholders = ",".join("?" for _ in message_ids)
        query = f"SELECT message_id FROM muted_messages WHERE message_id IN ({placeholders})"
        with self._connect() as conn:
            rows = conn.execute(query, message_ids).fetchall()

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

        return [signal_event_row_to_dict(raw) for raw in raw_rows]

    def latest_classification_for_message(
        self, message_id: str
    ) -> dict[str, str | float | int] | None:
        message_value = message_id.strip()
        if not message_value:
            return None

        with self._connect() as conn:
            raw = conn.execute(
                (
                    "SELECT message_id, thread_id, sender, subject, important, score, reason, "
                    "provider, model, classified_at "
                    "FROM classification_events "
                    "WHERE message_id = ? "
                    "ORDER BY id DESC LIMIT 1"
                ),
                (message_value,),
            ).fetchone()

        if raw is None:
            return None

        return classification_event_row_to_dict(raw)

    def record_feedback_correction(
        self,
        *,
        message_id: str,
        thread_id: str,
        original_important: bool,
        original_score: float,
        original_reason: str,
        corrected_important: bool,
        correction_source: str,
    ) -> None:
        message_value = message_id.strip()
        thread_value = thread_id.strip()
        source_value = correction_source.strip() or "telegram_button"
        reason_value = original_reason.strip() or "No reason provided"
        if not message_value or not thread_value:
            raise ValueError("message_id and thread_id are required.")

        with self._connect() as conn:
            conn.execute(
                (
                    "INSERT INTO feedback_corrections "
                    "(message_id, thread_id, original_important, original_score, original_reason, "
                    "corrected_important, correction_source) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)"
                ),
                (
                    message_value,
                    thread_value,
                    1 if original_important else 0,
                    float(max(0.0, min(1.0, original_score))),
                    reason_value,
                    1 if corrected_important else 0,
                    source_value,
                ),
            )

    def recent_feedback_corrections(self, limit: int = 20) -> list[dict[str, str | float | int]]:
        with self._connect() as conn:
            raw_rows = conn.execute(
                (
                    "SELECT id, message_id, thread_id, original_important, original_score, original_reason, "
                    "corrected_important, correction_source, created_at "
                    "FROM feedback_corrections "
                    "ORDER BY id DESC LIMIT ?"
                ),
                (limit,),
            ).fetchall()

        return [feedback_correction_row_to_dict(raw) for raw in raw_rows]

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            seen_count = conn.execute("SELECT COUNT(*) FROM seen_messages").fetchone()[0]
            signal_count = conn.execute("SELECT COUNT(*) FROM signal_events").fetchone()[0]
            classification_count = conn.execute(
                "SELECT COUNT(*) FROM classification_events"
            ).fetchone()[0]
            watch_rule_count = conn.execute(
                "SELECT COUNT(*) FROM watch_rules WHERE is_active = 1"
            ).fetchone()[0]
            watch_rule_event_count = conn.execute(
                "SELECT COUNT(*) FROM watch_rule_events"
            ).fetchone()[0]
            muted_thread_count = conn.execute("SELECT COUNT(*) FROM muted_threads").fetchone()[0]
            muted_message_count = conn.execute("SELECT COUNT(*) FROM muted_messages").fetchone()[0]
            vip_sender_count = conn.execute("SELECT COUNT(*) FROM vip_senders").fetchone()[0]
            feedback_correction_count = conn.execute(
                "SELECT COUNT(*) FROM feedback_corrections"
            ).fetchone()[0]

        return {
            "seen_messages": int(seen_count),
            "signal_events": int(signal_count),
            "classification_events": int(classification_count),
            "watch_rules": int(watch_rule_count),
            "watch_rule_events": int(watch_rule_event_count),
            "muted_threads": int(muted_thread_count),
            "muted_messages": int(muted_message_count),
            "vip_senders": int(vip_sender_count),
            "feedback_corrections": int(feedback_correction_count),
        }

    def _connect(self) -> sqlite3.Connection:
        logging.debug("Store: opening sqlite connection")
        return sqlite3.connect(self.db_path, timeout=30)
