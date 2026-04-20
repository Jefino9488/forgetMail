from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

try:
    from aiogram.types import CallbackQuery
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    CallbackQuery = Any

try:
    from forgetmail.embedding_client import EmbeddingClient
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback

    class _MissingEmbeddingDependency:
        @classmethod
        def from_config(cls, *_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError("embedding_client dependencies are not installed.")

    EmbeddingClient = _MissingEmbeddingDependency

from forgetmail.notifier import answer_callback_query
from forgetmail.store import StateStore

try:
    from forgetmail.vector_store import VectorStore
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback

    class _MissingVectorStore:
        @classmethod
        def from_config(cls, *_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError("vector_store dependencies are not installed.")

    VectorStore = _MissingVectorStore

from .telegram_io import _send_text_message


def _corrections_vector_store_from_config(
    embeddings_cfg: dict[str, Any],
) -> VectorStore:
    corrections_cfg = dict(embeddings_cfg)
    corrections_cfg["collection"] = (
        str(embeddings_cfg.get("corrections_collection", "email_corrections")).strip()
        or "email_corrections"
    )
    return VectorStore.from_config(corrections_cfg)


def _parse_feedback_callback_data(
    callback_data: str,
) -> tuple[str, str, str, str] | None:
    if callback_data.startswith("important:") or callback_data.startswith("notimportant:"):
        parts = callback_data.split(":", maxsplit=3)
        if len(parts) == 4:
            action = parts[0]
            message_id = parts[1].strip()
            thread_id = parts[2].strip()
            scope = parts[3].strip().lower()
            if scope not in {"message", "thread"}:
                scope = "thread"
            return action, message_id, thread_id, scope
        if len(parts) == 3:
            return parts[0], parts[1].strip(), parts[2].strip(), "thread"
        if len(parts) == 2 and parts[0] == "notimportant":
            return parts[0], "", parts[1].strip(), "thread"
    return None


def _upsert_feedback_correction_vector(
    *,
    config: dict[str, Any],
    message_id: str,
    thread_id: str,
    corrected_important: bool,
    correction_source: str,
    classification: dict[str, str | float | int] | None,
) -> None:
    embeddings_cfg = config.get("embeddings", {})
    if not bool(embeddings_cfg.get("enabled", False)):
        return
    if not bool(embeddings_cfg.get("enable_corrections", True)):
        return

    sender = str((classification or {}).get("sender", "unknown sender"))
    subject = str((classification or {}).get("subject", "(no subject)"))
    original_reason = str((classification or {}).get("reason", "No original reason"))
    original_important = int((classification or {}).get("important", 0))
    original_score = float((classification or {}).get("score", 0.0))
    corrected_label = 1 if corrected_important else 0

    correction_text = (
        f"From: {sender}\n"
        f"Subject: {subject}\n"
        f"Original important: {original_important} score: {original_score:.2f}\n"
        f"Original reason: {original_reason}\n"
        f"User corrected important: {corrected_label}"
    )

    embedding_client = EmbeddingClient.from_config(embeddings_cfg)
    embedding = embedding_client.embed_texts([correction_text])[0]
    correction_store = _corrections_vector_store_from_config(embeddings_cfg)
    now = datetime.now(timezone.utc).isoformat()
    correction_id = f"{message_id}:{int(datetime.now(timezone.utc).timestamp())}:{corrected_label}"
    correction_store.upsert_documents(
        ids=[correction_id],
        documents=[correction_text],
        embeddings=[embedding],
        metadatas=[
            {
                "message_id": message_id,
                "thread_id": thread_id,
                "sender": sender,
                "subject": subject,
                "original_important": original_important,
                "original_score": original_score,
                "original_reason": original_reason,
                "corrected_important": corrected_label,
                "correction_source": correction_source,
                "corrected_at": now,
            }
        ],
    )


def _handle_callback_query(
    *,
    token: str,
    config: dict[str, Any],
    store: StateStore,
    expected_chat_id: int,
    callback_query: CallbackQuery,
) -> None:
    callback_id = callback_query.id
    callback_data = callback_query.data
    message = callback_query.message
    if not callback_id:
        return
    if not isinstance(callback_data, str) or not callback_data:
        answer_callback_query(token, callback_id, "Unsupported action")
        return
    chat = getattr(message, "chat", None)
    chat_id = getattr(chat, "id", None)
    if not isinstance(chat_id, int):
        answer_callback_query(token, callback_id, "Unsupported action")
        return
    if chat_id != expected_chat_id:
        answer_callback_query(token, callback_id, "Action denied")
        return

    if callback_data.startswith("reply:"):
        answer_callback_query(token, callback_id, "Reply workflow coming soon")
        _send_text_message(
            store,
            token,
            expected_chat_id,
            "Reply action received. Reply workflow is coming soon.",
        )
        return

    if callback_data.startswith("undo:"):
        undo_parts = callback_data.split(":", maxsplit=2)
        if len(undo_parts) != 3:
            answer_callback_query(token, callback_id, "Invalid undo payload")
            return
        message_id = undo_parts[1].strip()
        thread_id = undo_parts[2].strip()
        unmuted_message = store.unmute_message(message_id) if message_id else False
        unmuted_thread = store.unmute_thread(thread_id) if thread_id else False
        if unmuted_message or unmuted_thread:
            answer_callback_query(token, callback_id, "Mute removed")
        else:
            answer_callback_query(token, callback_id, "Nothing to undo")
        return

    feedback_parts = _parse_feedback_callback_data(callback_data)
    if feedback_parts is not None:
        action, message_id, thread_id, scope = feedback_parts
        if not thread_id:
            answer_callback_query(token, callback_id, "Invalid thread id")
            return

        corrected_important = action == "important"

        classification = store.latest_classification_for_message(message_id) if message_id else None
        original_important = bool(int((classification or {}).get("important", 0)))
        original_score = float((classification or {}).get("score", 0.0))
        original_reason = str((classification or {}).get("reason", "No reason provided"))

        if action == "notimportant":
            if scope == "message":
                if not message_id:
                    answer_callback_query(token, callback_id, "Invalid message id")
                    return
                store.mute_message(message_id=message_id, thread_id=thread_id)
            else:
                store.mute_thread(thread_id=thread_id)
        else:
            store.unmute_thread(thread_id)
            if message_id:
                store.unmute_message(message_id)

        if message_id:
            try:
                store.record_feedback_correction(
                    message_id=message_id,
                    thread_id=thread_id,
                    original_important=original_important,
                    original_score=original_score,
                    original_reason=original_reason,
                    corrected_important=corrected_important,
                    correction_source=f"telegram_{action}_button_{scope}",
                )
                _upsert_feedback_correction_vector(
                    config=config,
                    message_id=message_id,
                    thread_id=thread_id,
                    corrected_important=corrected_important,
                    correction_source=f"telegram_{action}_button_{scope}",
                    classification=classification,
                )
            except Exception as exc:
                logging.warning("Feedback correction storage failed: %s", exc)

        if action == "notimportant":
            if scope == "message":
                answer_callback_query(token, callback_id, "Muted this email")
            else:
                answer_callback_query(token, callback_id, "Muted this thread")
            return

        answer_callback_query(token, callback_id, "Marked important")
        _send_text_message(
            store,
            token,
            expected_chat_id,
            "Marked as important. This correction will influence future classifications.",
        )
        return

    answer_callback_query(token, callback_id, "Unsupported action")
