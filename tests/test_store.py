from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from forgetmail.store import StateStore


class StoreFeedbackTests(unittest.TestCase):
    def test_feedback_corrections_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.record_classification_events(
                [
                    (
                        "m1",
                        "t1",
                        "alice@example.com",
                        "Need input",
                        0,
                        0.41,
                        "low priority",
                        "ollama",
                        "qwen2.5:3b",
                    )
                ]
            )

            latest = store.latest_classification_for_message("m1")
            self.assertIsNotNone(latest)
            self.assertEqual(latest["thread_id"], "t1")
            self.assertEqual(latest["important"], 0)

            store.record_feedback_correction(
                message_id="m1",
                thread_id="t1",
                original_important=False,
                original_score=0.41,
                original_reason="low priority",
                corrected_important=True,
                correction_source="telegram_important_button",
            )

            rows = store.recent_feedback_corrections(limit=5)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["corrected_important"], 1)

            stats = store.stats()
            self.assertEqual(stats["feedback_corrections"], 1)

    def test_unmute_thread(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()
            store.mute_thread("thread-x")
            self.assertTrue(store.unmute_thread("thread-x"))
            self.assertFalse(store.unmute_thread("thread-x"))

    def test_mute_and_unmute_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.mute_message("m-1", "t-1")
            self.assertEqual(store.muted_messages(["m-1", "m-2"]), {"m-1"})

            self.assertTrue(store.unmute_message("m-1"))
            self.assertFalse(store.unmute_message("m-1"))

    def test_stats_include_muted_messages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.mute_message("m-10", "t-10")
            stats = store.stats()
            self.assertEqual(stats.get("muted_messages"), 1)

    def test_vip_sender_roundtrip_normalizes_address(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.add_vip_sender("john@company.com", "John Smith")

            vip_rows = store.list_vip_senders()
            self.assertEqual(len(vip_rows), 1)
            self.assertEqual(vip_rows[0]["sender_email"], "john@company.com")

            self.assertEqual(store.vip_senders(["john@company.com"]), {"john@company.com"})
            self.assertTrue(store.remove_vip_sender("John Smith <john@company.com>"))

    def test_cache_value_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.set_cache_value("heartbeat_last_sent_date", "2026-04-20")
            self.assertEqual(store.get_cache_value("heartbeat_last_sent_date"), "2026-04-20")
            store.delete_cache_value("heartbeat_last_sent_date")
            self.assertIsNone(store.get_cache_value("heartbeat_last_sent_date"))


if __name__ == "__main__":
    unittest.main()
