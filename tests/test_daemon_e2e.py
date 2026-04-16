from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from forgetmail import daemon
from forgetmail.store import StateStore


class _FakeEmbeddingClient:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.11, 0.22] for _ in texts]


class _FakeVectorStore:
    def query_similar(self, _query_embedding: list[float], *, top_k: int = 5) -> dict:
        return {
            "ids": [["m1", "m2"]],
            "metadatas": [
                [
                    {
                        "subject": "Budget request",
                        "sender": "alice@example.com",
                        "snippet": "Need budget by EOD",
                        "reason": "finance",
                    },
                    {
                        "subject": "Roadmap",
                        "sender": "bob@example.com",
                        "snippet": "Quarterly roadmap draft",
                        "reason": "planning",
                    },
                ]
            ],
            "distances": [[0.10, 0.25]],
        }


class DaemonE2ETests(unittest.TestCase):
    def test_ask_command_end_to_end_sends_answer(self) -> None:
        config = {
            "llm": {
                "ask_enabled": True,
                "ask_top_k": 6,
                "ask_timeout_seconds": 30,
                "ask_max_context_chars": 3000,
                "ask_max_citations": 3,
            },
            "embeddings": {
                "enabled": True,
            },
        }

        sent_messages: list[tuple[str, int, str]] = []

        with (
            patch(
                "forgetmail.daemon.EmbeddingClient.from_config",
                return_value=_FakeEmbeddingClient(),
            ),
            patch(
                "forgetmail.daemon.VectorStore.from_config",
                return_value=_FakeVectorStore(),
            ),
            patch(
                "forgetmail.daemon.call_answer_json",
                return_value={
                    "answer": "Budget info is in Alice's message.",
                    "confidence": 0.87,
                    "citations": [
                        {
                            "message_id": "m1",
                            "subject": "Budget request",
                            "why": "contains budget deadline",
                        }
                    ],
                },
            ),
            patch(
                "forgetmail.daemon.send_text_message",
                side_effect=lambda token, chat_id, text: sent_messages.append(
                    (token, chat_id, text)
                ),
            ),
        ):
            daemon._handle_ask_command(
                token="tg-token",
                expected_chat_id=123,
                text="/ask where is the latest budget request",
                config=config,
            )

        self.assertEqual(len(sent_messages), 1)
        _token, chat_id, text = sent_messages[0]
        self.assertEqual(chat_id, 123)
        self.assertIn("A: Budget info is in Alice's message.", text)
        self.assertIn("Sources:", text)
        self.assertIn("[m1]", text)

    def test_feedback_callback_important_records_correction_and_unmutes(self) -> None:
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
                        "Need your review",
                        0,
                        0.42,
                        "low confidence",
                        "ollama",
                        "qwen2.5:3b",
                    )
                ]
            )
            store.mute_thread("t1")

            callback_query = SimpleNamespace(
                id="cb-1",
                data="important:m1:t1",
                message=SimpleNamespace(chat=SimpleNamespace(id=123)),
            )

            sent_messages: list[str] = []
            callback_acks: list[str] = []

            with (
                patch(
                    "forgetmail.daemon._upsert_feedback_correction_vector",
                    return_value=None,
                ),
                patch(
                    "forgetmail.daemon.send_text_message",
                    side_effect=lambda _token, _chat_id, text: sent_messages.append(text),
                ),
                patch(
                    "forgetmail.daemon.answer_callback_query",
                    side_effect=lambda _token, _cb_id, text: callback_acks.append(text),
                ),
            ):
                daemon._handle_callback_query(
                    token="tg-token",
                    config={"embeddings": {"enabled": False}},
                    store=store,
                    expected_chat_id=123,
                    callback_query=callback_query,
                )

            rows = store.recent_feedback_corrections(limit=5)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["message_id"], "m1")
            self.assertEqual(rows[0]["thread_id"], "t1")
            self.assertEqual(rows[0]["corrected_important"], 1)
            self.assertEqual(store.muted_threads(["t1"]), set())
            self.assertIn("Marked important", callback_acks)
            self.assertTrue(any("influence future classifications" in msg for msg in sent_messages))

    def test_feedback_callback_notimportant_records_correction_and_mutes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.record_classification_events(
                [
                    (
                        "m2",
                        "t2",
                        "bob@example.com",
                        "Action required",
                        1,
                        0.91,
                        "urgent action",
                        "ollama",
                        "qwen2.5:3b",
                    )
                ]
            )

            callback_query = SimpleNamespace(
                id="cb-2",
                data="notimportant:m2:t2",
                message=SimpleNamespace(chat=SimpleNamespace(id=123)),
            )

            with (
                patch(
                    "forgetmail.daemon._upsert_feedback_correction_vector",
                    return_value=None,
                ),
                patch("forgetmail.daemon.send_text_message", return_value=None),
                patch("forgetmail.daemon.answer_callback_query", return_value=None),
            ):
                daemon._handle_callback_query(
                    token="tg-token",
                    config={"embeddings": {"enabled": False}},
                    store=store,
                    expected_chat_id=123,
                    callback_query=callback_query,
                )

            rows = store.recent_feedback_corrections(limit=5)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["message_id"], "m2")
            self.assertEqual(rows[0]["corrected_important"], 0)
            self.assertEqual(store.muted_threads(["t2"]), {"t2"})


if __name__ == "__main__":
    unittest.main()
