from __future__ import annotations

import logging
from typing import Any

try:
    from forgetmail.embedding_client import EmbeddingClient
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback

    class _MissingEmbeddingDependency:
        @classmethod
        def from_config(cls, *_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError("embedding_client dependencies are not installed.")

    EmbeddingClient = _MissingEmbeddingDependency

try:
    from forgetmail.llm import call_answer_json
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback

    def call_answer_json(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("llm dependencies are not installed.")


try:
    from forgetmail.vector_store import VectorStore
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback

    class _MissingVectorStore:
        @classmethod
        def from_config(cls, *_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError("vector_store dependencies are not installed.")

    VectorStore = _MissingVectorStore

from forgetmail.store import StateStore

from .common import _distance_to_similarity
from .commands import _extract_command_payload
from .telegram_io import _send_text_message, _send_text_message_with_url_button


def _gmail_thread_url(thread_id: str) -> str:
    return f"https://mail.google.com/mail/u/0/#all/{thread_id}"


def _resolve_top_source_url(
    payload: dict[str, Any],
    thread_ids_by_message_id: dict[str, str] | None,
) -> str:
    citations = payload.get("citations", [])
    if not isinstance(citations, list) or not citations:
        return ""
    if not isinstance(thread_ids_by_message_id, dict):
        return ""

    first_citation = citations[0]
    if not isinstance(first_citation, dict):
        return ""

    first_message_id = str(first_citation.get("message_id", "")).strip()
    if not first_message_id:
        return ""

    thread_id = thread_ids_by_message_id.get(first_message_id, "")
    if not thread_id:
        return ""

    return _gmail_thread_url(thread_id)


def _format_ask_response(
    question: str,
    payload: dict[str, Any],
    *,
    thread_ids_by_message_id: dict[str, str] | None = None,
    min_confidence: float = 0.5,
) -> str:
    answer = str(payload.get("answer", "")).strip()
    confidence = float(payload.get("confidence", 0.0))
    citations = payload.get("citations", [])

    if not answer:
        return "Could not produce an answer from your inbox context."

    clamped_min_confidence = max(0.0, min(1.0, float(min_confidence)))
    is_low_confidence = confidence < clamped_min_confidence
    lines = [f"Q: {question}"]
    if is_low_confidence:
        lines.append(f"A: unsure ({answer})")
        lines.append(f"Confidence: {confidence:.2f} (low)")
    else:
        lines.append(f"A: {answer}")
        lines.append(f"Confidence: {confidence:.2f}")

    top_source_url = _resolve_top_source_url(payload, thread_ids_by_message_id)
    if isinstance(citations, list) and citations:
        if top_source_url:
            lines.append(f"Open top source: {top_source_url}")
        lines.append("Sources:")
        for item in citations:
            if not isinstance(item, dict):
                continue
            message_id = str(item.get("message_id", "")).strip()
            subject = str(item.get("subject", "(no subject)")).strip() or "(no subject)"
            why = str(item.get("why", "relevant context")).strip() or "relevant context"
            if not message_id:
                continue
            source_line = f"- [{message_id}] {subject} ({why})"
            if isinstance(thread_ids_by_message_id, dict):
                thread_id = thread_ids_by_message_id.get(message_id, "")
                if thread_id:
                    source_line = f"{source_line} -> {_gmail_thread_url(thread_id)}"
            lines.append(source_line)

    if is_low_confidence:
        lines.append(
            "Tip: refine your query with sender, timeframe, or exact keyword for better accuracy."
        )
    return "\n".join(lines)


def _build_ask_context_rows(
    *,
    query_results: dict[str, Any],
    max_context_chars: int,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    ids_rows = query_results.get("ids")
    metadata_rows = query_results.get("metadatas")
    distance_rows = query_results.get("distances")
    if not isinstance(ids_rows, list) or not ids_rows:
        return [], {}

    first_ids = ids_rows[0] if isinstance(ids_rows[0], list) else []
    first_meta = (
        metadata_rows[0]
        if isinstance(metadata_rows, list) and metadata_rows and isinstance(metadata_rows[0], list)
        else []
    )
    first_distances = (
        distance_rows[0]
        if isinstance(distance_rows, list) and distance_rows and isinstance(distance_rows[0], list)
        else []
    )

    context_rows: list[dict[str, Any]] = []
    thread_ids_by_message_id: dict[str, str] = {}
    used_chars = 0
    for index, raw_id in enumerate(first_ids):
        if not isinstance(raw_id, str) or not raw_id.strip():
            continue

        metadata = first_meta[index] if index < len(first_meta) else None
        if not isinstance(metadata, dict):
            metadata = {}

        subject = str(metadata.get("subject", "(no subject)")).strip() or "(no subject)"
        sender = str(metadata.get("sender", "unknown")).strip() or "unknown"
        snippet = str(metadata.get("snippet", "")).strip()
        reason = str(metadata.get("reason", "")).strip()
        similarity = (
            _distance_to_similarity(
                first_distances[index] if index < len(first_distances) else None
            )
            or 0.0
        )

        row = {
            "message_id": raw_id,
            "subject": subject,
            "sender": sender,
            "snippet": snippet,
            "reason": reason,
            "similarity": round(similarity, 4),
        }
        thread_id = str(metadata.get("thread_id", "")).strip()
        if thread_id:
            thread_ids_by_message_id[raw_id] = thread_id
        row_chars = len(subject) + len(sender) + len(snippet) + len(reason)
        if context_rows and used_chars + row_chars > max_context_chars:
            break
        context_rows.append(row)
        used_chars += row_chars

    return context_rows, thread_ids_by_message_id


def _handle_ask_command(
    *,
    token: str,
    expected_chat_id: int,
    text: str,
    config: dict[str, Any],
    store: StateStore,
) -> None:
    question = _extract_command_payload(text)
    if not question:
        _send_text_message(store, token, expected_chat_id, "Usage: /ask <question>")
        return

    llm_cfg = config["llm"]
    if not bool(llm_cfg.get("ask_enabled", True)):
        _send_text_message(
            store,
            token,
            expected_chat_id,
            "Ask command is disabled in config (llm.ask_enabled=false).",
        )
        return

    embeddings_cfg = config.get("embeddings", {})
    if not bool(embeddings_cfg.get("enabled", False)):
        _send_text_message(
            store,
            token,
            expected_chat_id,
            "Ask needs embeddings.enabled=true to search your inbox vectors.",
        )
        return

    try:
        embedding_client = EmbeddingClient.from_config(embeddings_cfg)
        vector_store = VectorStore.from_config(embeddings_cfg)
        query_embedding = embedding_client.embed_texts([question])[0]
        query_results = vector_store.query_similar(
            query_embedding,
            top_k=max(1, int(llm_cfg.get("ask_top_k", 6))),
        )
        context_rows, thread_ids_by_message_id = _build_ask_context_rows(
            query_results=query_results,
            max_context_chars=max(500, int(llm_cfg.get("ask_max_context_chars", 3500))),
        )
    except Exception as exc:
        logging.warning("Ask retrieval failed: %s", exc)
        _send_text_message(
            store,
            token,
            expected_chat_id,
            "Could not retrieve inbox context right now.",
        )
        return

    if not context_rows:
        _send_text_message(
            store,
            token,
            expected_chat_id,
            "No relevant email context found yet. Try again after more mail is indexed.",
        )
        return

    try:
        answer_payload = call_answer_json(
            llm_cfg,
            question=question,
            context_rows=context_rows,
            timeout_seconds=max(5, int(llm_cfg.get("ask_timeout_seconds", 90))),
        )
        response_text = _format_ask_response(
            question,
            answer_payload,
            thread_ids_by_message_id=thread_ids_by_message_id,
            min_confidence=float(llm_cfg.get("ask_min_confidence", 0.5)),
        )
        top_source_url = _resolve_top_source_url(answer_payload, thread_ids_by_message_id)
        if top_source_url:
            _send_text_message_with_url_button(
                store,
                token,
                expected_chat_id,
                response_text,
                button_text="Open top source",
                url=top_source_url,
            )
        else:
            _send_text_message(store, token, expected_chat_id, response_text)
    except Exception as exc:
        logging.warning("Ask answer generation failed: %s", exc)
        _send_text_message(
            store,
            token,
            expected_chat_id,
            "I could not generate a safe structured answer this time.",
        )
