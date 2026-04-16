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
                        "thread_id": "t1",
                    },
                    {
                        "subject": "Roadmap",
                        "sender": "bob@example.com",
                        "snippet": "Quarterly roadmap draft",
                        "reason": "planning",
                        "thread_id": "t2",
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
                "ask_min_confidence": 0.5,
            },
            "embeddings": {
                "enabled": True,
            },
        }

        sent_messages: list[tuple[str, int, str]] = []
        sent_button_messages: list[tuple[str, int, str, str, str]] = []

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
            patch(
                "forgetmail.daemon.send_text_message_with_url_button",
                side_effect=lambda token, chat_id, text, *, button_text, url: (
                    sent_button_messages.append((token, chat_id, text, button_text, url))
                ),
            ),
        ):
            daemon._handle_ask_command(
                token="tg-token",
                expected_chat_id=123,
                text="/ask where is the latest budget request",
                config=config,
            )

        self.assertEqual(len(sent_messages), 0)
        self.assertEqual(len(sent_button_messages), 1)
        _token, chat_id, text, button_text, button_url = sent_button_messages[0]
        self.assertEqual(chat_id, 123)
        self.assertIn("A: Budget info is in Alice's message.", text)
        self.assertIn("Sources:", text)
        self.assertIn("[m1]", text)
        self.assertIn("Open top source: https://mail.google.com/mail/u/0/#all/t1", text)
        self.assertIn("https://mail.google.com/mail/u/0/#all/t1", text)
        self.assertEqual(button_text, "Open top source")
        self.assertEqual(button_url, "https://mail.google.com/mail/u/0/#all/t1")

    def test_ask_command_low_confidence_shows_unsure_hint(self) -> None:
        config = {
            "llm": {
                "ask_enabled": True,
                "ask_top_k": 6,
                "ask_timeout_seconds": 30,
                "ask_max_context_chars": 3000,
                "ask_max_citations": 3,
                "ask_min_confidence": 0.7,
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
                    "answer": "There might be one related result.",
                    "confidence": 0.42,
                    "citations": [
                        {
                            "message_id": "m1",
                            "subject": "Budget request",
                            "why": "keyword match",
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
            patch(
                "forgetmail.daemon.send_text_message_with_url_button",
                return_value=None,
            ),
        ):
            daemon._handle_ask_command(
                token="tg-token",
                expected_chat_id=123,
                text="/ask anything about budget",
                config=config,
            )

        self.assertEqual(len(sent_messages), 1)
        _token, chat_id, text = sent_messages[0]
        self.assertEqual(chat_id, 123)
        self.assertIn("A: unsure", text)
        self.assertIn("Confidence: 0.42 (low)", text)
        self.assertIn("Tip: refine your query", text)

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
            store.mute_message("m1", "t1")

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
            self.assertEqual(store.muted_messages(["m1"]), set())
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
                data="notimportant:m2:t2:thread",
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
            self.assertEqual(rows[0]["message_id"], "m2")
            self.assertEqual(rows[0]["corrected_important"], 0)
            self.assertEqual(store.muted_threads(["t2"]), {"t2"})
            self.assertIn("Muted this thread", callback_acks)
            self.assertEqual(sent_messages, [])

    def test_feedback_callback_notimportant_message_scope_mutes_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.record_classification_events(
                [
                    (
                        "m3",
                        "t3",
                        "carol@example.com",
                        "FYI",
                        1,
                        0.83,
                        "contains urgent keyword",
                        "ollama",
                        "qwen2.5:3b",
                    )
                ]
            )

            callback_query = SimpleNamespace(
                id="cb-3",
                data="notimportant:m3:t3:message",
                message=SimpleNamespace(chat=SimpleNamespace(id=123)),
            )

            callback_acks: list[str] = []

            with (
                patch(
                    "forgetmail.daemon._upsert_feedback_correction_vector",
                    return_value=None,
                ),
                patch("forgetmail.daemon.send_text_message", return_value=None),
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

            self.assertEqual(store.muted_messages(["m3"]), {"m3"})
            self.assertEqual(store.muted_threads(["t3"]), set())
            self.assertIn("Muted this email", callback_acks)

    def test_undo_callback_unmutes_thread_and_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "state.db"
            store = StateStore(db_path=db_path)
            store.initialize()

            store.mute_thread("t9")
            store.mute_message("m9", "t9")

            callback_query = SimpleNamespace(
                id="cb-9",
                data="undo:m9:t9",
                message=SimpleNamespace(chat=SimpleNamespace(id=123)),
            )

            callback_acks: list[str] = []

            with (
                patch("forgetmail.daemon.send_text_message", return_value=None),
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

            self.assertEqual(store.muted_messages(["m9"]), set())
            self.assertEqual(store.muted_threads(["t9"]), set())
            self.assertIn("Mute removed", callback_acks)


if __name__ == "__main__":
    unittest.main()
