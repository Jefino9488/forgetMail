import logging
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aiogram.types import CallbackQuery, Update

from forgetmail.auth.telegram import get_bot_token
from forgetmail.embedding_client import (
    EmbeddingClient,
    EmbeddingError,
    candidate_to_embedding_text,
)
from forgetmail.classifier import LLMError
from forgetmail.classifier import classify_messages
from forgetmail.config import load_config
from .polling import poll_once as _poll_once_impl
from forgetmail.llm import call_answer_json
from forgetmail.notifier import (
    SignalNotification,
    answer_callback_query,
    configure_bot_commands,
    fetch_updates,
    prepare_polling_mode,
    send_signal_notifications,
    send_text_message,
    shutdown_client,
)
from forgetmail.poller import (
    fetch_message_candidates,
    list_recent_unread_message_ids,
    mark_messages_read,
)
from forgetmail.store import StateStore
from forgetmail.vector_store import VectorStore, VectorStoreError

OMITTED_REASON = "Classifier omitted this message"


def _setup_logging(
    level_name: str,
    debug: bool = False,
    log_file: str | None = None,
    http_debug: bool = False,
) -> None:
    level = (
        logging.DEBUG if debug else getattr(logging, level_name.upper(), logging.INFO)
    )
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if isinstance(log_file, str) and log_file.strip():
        file_path = Path(log_file).expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(file_path, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
        force=True,
    )
    if not http_debug:
        for logger_name in (
            "httpcore",
            "httpx",
            "urllib3",
            "keyring",
            "google.auth.transport.requests",
        ):
            logging.getLogger(logger_name).setLevel(logging.WARNING)


def _build_signals(
    messages, classifications, threshold: float
) -> list[SignalNotification]:
    class_map = {item.message_id: item for item in classifications}
    signals: list[SignalNotification] = []
    for message in messages:
        result = class_map.get(message.message_id)
        if not result:
            continue
        if result.important and result.score >= threshold:
            signals.append(
                SignalNotification(
                    message_id=message.message_id,
                    thread_id=message.thread_id,
                    sender=message.sender,
                    subject=message.subject,
                    reason=result.reason,
                    score=result.score,
                )
            )
    return signals


def _help_text() -> str:
    return (
        "forgetMail bot commands:\n"
        "/help - show this help\n"
        "/status - runtime and DB stats\n"
        "/signals - show recent signal notifications\n"
        "/ask <question> - chat with your inbox\n"
        "/watchFor <context> [boost] - prioritize matching emails\n"
        "/watchList - list active watch rules\n"
        "/unwatch <rule_id> - delete a watch rule\n"
        "/run - trigger an immediate poll cycle"
    )


def _format_recent_signals(rows: list[dict[str, str | float]]) -> str:
    if not rows:
        return "No signal notifications recorded yet."

    lines = ["Recent signals:"]
    for item in rows:
        lines.append(
            (
                f"- {item['notified_at']} | {item['subject']} | score={float(item['score']):.2f}"
            )
        )
    return "\n".join(lines)


def _format_status(
    config: dict[str, Any], store: StateStore, last_cycle: dict[str, int] | None
) -> str:
    stats = store.stats()
    llm_cfg = config["llm"]
    embeddings_cfg = config.get("embeddings", {})
    gmail_cfg = config["gmail"]
    lines = [
        "forgetMail status:",
        f"- poll_interval_seconds: {gmail_cfg['poll_interval_seconds']}",
        f"- idle_poll_interval_seconds: {gmail_cfg.get('idle_poll_interval_seconds', gmail_cfg['poll_interval_seconds'])}",
        f"- lookback_days: {gmail_cfg['lookback_days']}",
        f"- max_messages_per_poll: {gmail_cfg['max_messages_per_poll']}",
        f"- llm_provider: {llm_cfg['provider']}",
        f"- llm_model: {llm_cfg['model']}",
        f"- llm_prompt_style: {llm_cfg.get('prompt_style', 'caveman')}",
        f"- importance_threshold: {llm_cfg['importance_threshold']}",
        f"- embeddings_enabled: {bool(embeddings_cfg.get('enabled', False))}",
        f"- embeddings_model: {embeddings_cfg.get('model', 'n/a')}",
        f"- vector_upsert_enabled: {bool(embeddings_cfg.get('enable_vector_upsert', False))}",
        f"- vector_query_enabled: {bool(embeddings_cfg.get('enable_vector_query', False))}",
        f"- vector_query_top_k: {embeddings_cfg.get('query_top_k', 'n/a')}",
        f"- seen_messages: {stats['seen_messages']}",
        f"- signal_events: {stats['signal_events']}",
        f"- classification_events: {stats['classification_events']}",
        f"- watch_rules: {stats['watch_rules']}",
        f"- watch_rule_events: {stats['watch_rule_events']}",
        f"- muted_threads: {stats['muted_threads']}",
        f"- feedback_corrections: {stats.get('feedback_corrections', 0)}",
    ]

    if last_cycle:
        lines.append(
            (
                "- last_cycle: "
                f"fetched={last_cycle['fetched']} unseen={last_cycle['unseen']} "
                f"classified={last_cycle['classified']} "
                f"boosted={last_cycle['boosted']} "
                f"signals={last_cycle['signals']} sent={last_cycle['sent']} "
                f"gmail_marked_read={last_cycle.get('gmail_marked_read', 0)} "
                f"vector_boosted={last_cycle.get('vector_boosted', 0)} "
                f"few_shot_examples={last_cycle.get('few_shot_examples', 0)} "
                f"omitted_for_retry={last_cycle.get('omitted_for_retry', 0)} "
                f"marked_seen={last_cycle['marked_seen']} llm_failed={last_cycle['llm_failed']}"
            )
        )

    return "\n".join(lines)


def _format_watch_rules(store: StateStore) -> str:
    rows = store.list_watch_rules(active_only=True)
    if not rows:
        return "No active watch rules. Add one with /watchFor <context> [boost]"

    lines = ["Active watch rules:"]
    for item in rows[:20]:
        lines.append(
            (
                f"- id={item['id']} context={item['context']} boost={float(item['boost']):.2f}"
            )
        )
    return "\n".join(lines)


def _handle_watch_for(text: str, store: StateStore) -> str:
    parts = text.strip().split()
    if len(parts) < 2:
        return "Usage: /watchFor <context> [boost]"

    payload = text.strip().split(maxsplit=1)[1].strip()
    if not payload:
        return "Usage: /watchFor <context> [boost]"

    context = payload
    boost = 0.20
    payload_parts = payload.rsplit(" ", maxsplit=1)
    if len(payload_parts) == 2:
        maybe_boost = payload_parts[1].strip()
        try:
            boost_value = float(maybe_boost)
            if 0.0 <= boost_value <= 1.0:
                boost = boost_value
                context = payload_parts[0].strip()
        except ValueError:
            pass

    if not context:
        return "Usage: /watchFor <context> [boost]"

    rule_id = store.add_watch_rule(context=context, boost=boost)
    return f"Watch rule created: id={rule_id} context={context} boost={boost:.2f}"


def _parse_unwatch_command(text: str) -> int | None:
    parts = text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1].strip())
    except ValueError:
        return None


def _extract_command_payload(text: str) -> str:
    parts = text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return ""
    return parts[1].strip()


def _corrections_vector_store_from_config(
    embeddings_cfg: dict[str, Any],
) -> VectorStore:
    corrections_cfg = dict(embeddings_cfg)
    corrections_cfg["collection"] = (
        str(embeddings_cfg.get("corrections_collection", "email_corrections")).strip()
        or "email_corrections"
    )
    return VectorStore.from_config(corrections_cfg)


def _format_ask_response(question: str, payload: dict[str, Any]) -> str:
    answer = str(payload.get("answer", "")).strip()
    confidence = float(payload.get("confidence", 0.0))
    citations = payload.get("citations", [])
    if not answer:
        return "Could not produce an answer from your inbox context."

    lines = [f"Q: {question}", f"A: {answer}", f"Confidence: {confidence:.2f}"]
    if isinstance(citations, list) and citations:
        lines.append("Sources:")
        for item in citations:
            if not isinstance(item, dict):
                continue
            message_id = str(item.get("message_id", "")).strip()
            subject = str(item.get("subject", "(no subject)")).strip() or "(no subject)"
            why = str(item.get("why", "relevant context")).strip() or "relevant context"
            if not message_id:
                continue
            lines.append(f"- [{message_id}] {subject} ({why})")
    return "\n".join(lines)


def _build_ask_context_rows(
    *,
    query_results: dict[str, Any],
    max_context_chars: int,
) -> list[dict[str, Any]]:
    ids_rows = query_results.get("ids")
    metadata_rows = query_results.get("metadatas")
    distance_rows = query_results.get("distances")
    if not isinstance(ids_rows, list) or not ids_rows:
        return []

    first_ids = ids_rows[0] if isinstance(ids_rows[0], list) else []
    first_meta = (
        metadata_rows[0]
        if isinstance(metadata_rows, list)
        and metadata_rows
        and isinstance(metadata_rows[0], list)
        else []
    )
    first_distances = (
        distance_rows[0]
        if isinstance(distance_rows, list)
        and distance_rows
        and isinstance(distance_rows[0], list)
        else []
    )

    context_rows: list[dict[str, Any]] = []
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
        row_chars = len(subject) + len(sender) + len(snippet) + len(reason)
        if context_rows and used_chars + row_chars > max_context_chars:
            break
        context_rows.append(row)
        used_chars += row_chars

    return context_rows


def _handle_ask_command(
    *,
    token: str,
    expected_chat_id: int,
    text: str,
    config: dict[str, Any],
) -> None:
    question = _extract_command_payload(text)
    if not question:
        send_text_message(token, expected_chat_id, "Usage: /ask <question>")
        return

    llm_cfg = config["llm"]
    if not bool(llm_cfg.get("ask_enabled", True)):
        send_text_message(
            token,
            expected_chat_id,
            "Ask command is disabled in config (llm.ask_enabled=false).",
        )
        return

    embeddings_cfg = config.get("embeddings", {})
    if not bool(embeddings_cfg.get("enabled", False)):
        send_text_message(
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
        context_rows = _build_ask_context_rows(
            query_results=query_results,
            max_context_chars=max(500, int(llm_cfg.get("ask_max_context_chars", 3500))),
        )
    except Exception as exc:
        logging.warning("Ask retrieval failed: %s", exc)
        send_text_message(
            token, expected_chat_id, "Could not retrieve inbox context right now."
        )
        return

    if not context_rows:
        send_text_message(
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
        send_text_message(
            token, expected_chat_id, _format_ask_response(question, answer_payload)
        )
    except Exception as exc:
        logging.warning("Ask answer generation failed: %s", exc)
        send_text_message(
            token,
            expected_chat_id,
            "I could not generate a safe structured answer this time.",
        )


def _parse_feedback_callback_data(callback_data: str) -> tuple[str, str, str] | None:
    if callback_data.startswith("important:") or callback_data.startswith(
        "notimportant:"
    ):
        parts = callback_data.split(":", maxsplit=2)
        if len(parts) == 3:
            return parts[0], parts[1].strip(), parts[2].strip()
        # Backward compatibility for older callback format: notimportant:<thread_id>
        if len(parts) == 2 and parts[0] == "notimportant":
            return parts[0], "", parts[1].strip()
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
    correction_id = (
        f"{message_id}:{int(datetime.now(timezone.utc).timestamp())}:{corrected_label}"
    )
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


def _build_correction_few_shot_examples(
    *,
    correction_store: VectorStore,
    candidates: list[Any],
    embeddings_by_message_id: dict[str, list[float]],
    embeddings_cfg: dict[str, Any],
    llm_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    if not candidates or not embeddings_by_message_id:
        return []

    max_examples = max(0, int(llm_cfg.get("few_shot_max_examples", 4)))
    if max_examples == 0:
        return []

    query_top_k = max(1, int(embeddings_cfg.get("corrections_top_k", 2)))
    min_similarity = float(embeddings_cfg.get("corrections_min_similarity", 0.72))
    min_similarity = max(0.0, min(1.0, min_similarity))

    ordered_embeddings = [
        embeddings_by_message_id[item.message_id]
        for item in candidates
        if item.message_id in embeddings_by_message_id
    ]
    if len(ordered_embeddings) != len(candidates):
        return []

    results = correction_store.query_similar_by_embeddings(
        ordered_embeddings, top_k=query_top_k
    )
    ids_rows = results.get("ids")
    metadata_rows = results.get("metadatas")
    documents_rows = results.get("documents")
    distance_rows = results.get("distances")
    if not isinstance(ids_rows, list) or not isinstance(metadata_rows, list):
        return []

    by_correction_id: dict[str, tuple[float, dict[str, Any]]] = {}
    for index in range(len(candidates)):
        row_ids = (
            ids_rows[index]
            if index < len(ids_rows) and isinstance(ids_rows[index], list)
            else []
        )
        row_meta = (
            metadata_rows[index]
            if index < len(metadata_rows) and isinstance(metadata_rows[index], list)
            else []
        )
        row_docs = (
            documents_rows[index]
            if isinstance(documents_rows, list)
            and index < len(documents_rows)
            and isinstance(documents_rows[index], list)
            else []
        )
        row_distances = (
            distance_rows[index]
            if isinstance(distance_rows, list)
            and index < len(distance_rows)
            and isinstance(distance_rows[index], list)
            else []
        )

        for item_index, correction_id in enumerate(row_ids):
            if not isinstance(correction_id, str) or not correction_id:
                continue

            similarity = _distance_to_similarity(
                row_distances[item_index] if item_index < len(row_distances) else None
            )
            if similarity is None or similarity < min_similarity:
                continue

            metadata = row_meta[item_index] if item_index < len(row_meta) else None
            if not isinstance(metadata, dict):
                continue

            try:
                corrected_important = int(metadata.get("corrected_important", 0)) == 1
            except (TypeError, ValueError):
                corrected_important = False
            reason = (
                str(metadata.get("original_reason", "user correction")).strip()
                or "user correction"
            )

            text = ""
            if item_index < len(row_docs) and isinstance(row_docs[item_index], str):
                text = row_docs[item_index]
            text = " ".join(text.split())
            if not text:
                continue

            example = {
                "important": corrected_important,
                "reason": reason[:140],
                "text": text[:220],
            }
            previous = by_correction_id.get(correction_id)
            if previous is None or similarity > previous[0]:
                by_correction_id[correction_id] = (similarity, example)

    sorted_examples = sorted(
        by_correction_id.values(), key=lambda item: item[0], reverse=True
    )
    return [item[1] for item in sorted_examples[:max_examples]]


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
        send_text_message(
            token,
            expected_chat_id,
            "Reply action received. Reply workflow is coming soon.",
        )
        return

    feedback_parts = _parse_feedback_callback_data(callback_data)
    if feedback_parts is not None:
        action, message_id, thread_id = feedback_parts
        if not thread_id:
            answer_callback_query(token, callback_id, "Invalid thread id")
            return

        corrected_important = action == "important"

        classification = (
            store.latest_classification_for_message(message_id) if message_id else None
        )
        original_important = bool(int((classification or {}).get("important", 0)))
        original_score = float((classification or {}).get("score", 0.0))
        original_reason = str(
            (classification or {}).get("reason", "No reason provided")
        )

        if action == "notimportant":
            store.mute_thread(thread_id=thread_id)
        else:
            store.unmute_thread(thread_id)

        if message_id:
            try:
                store.record_feedback_correction(
                    message_id=message_id,
                    thread_id=thread_id,
                    original_important=original_important,
                    original_score=original_score,
                    original_reason=original_reason,
                    corrected_important=corrected_important,
                    correction_source=f"telegram_{action}_button",
                )
                _upsert_feedback_correction_vector(
                    config=config,
                    message_id=message_id,
                    thread_id=thread_id,
                    corrected_important=corrected_important,
                    correction_source=f"telegram_{action}_button",
                    classification=classification,
                )
            except Exception as exc:
                logging.warning("Feedback correction storage failed: %s", exc)

        if action == "notimportant":
            answer_callback_query(token, callback_id, "Marked not important")
            send_text_message(
                token,
                expected_chat_id,
                "Marked thread as not important. Future notifications for this thread are suppressed.",
            )
            return

        answer_callback_query(token, callback_id, "Marked important")
        send_text_message(
            token,
            expected_chat_id,
            "Marked as important. This correction will influence future classifications.",
        )
        return

    answer_callback_query(token, callback_id, "Unsupported action")


def _normalize_command(text: str) -> str:
    head = text.strip().split(maxsplit=1)[0].lower()
    return head.split("@", maxsplit=1)[0]


def _looks_like_newsletter(sender: str, subject: str, snippet: str) -> bool:
    merged = f"{sender} {subject} {snippet}".lower()
    newsletter_markers = [
        "newsletter",
        "digest",
        "unsubscribe",
        "sponsored",
        "promotion",
        "theresanaiforthat",
    ]
    personal_markers = [
        "can you",
        "please",
        "asap",
        "urgent",
        "meeting",
        "schedule",
        "reply",
        "action required",
    ]
    has_newsletter_signal = any(item in merged for item in newsletter_markers)
    has_personal_signal = any(item in merged for item in personal_markers)
    return has_newsletter_signal and not has_personal_signal


def _select_poll_interval_seconds(
    *,
    active_interval_seconds: int,
    idle_interval_seconds: int,
    last_cycle: dict[str, int] | None,
) -> int:
    if not last_cycle:
        return active_interval_seconds
    if int(last_cycle.get("llm_failed", 0)) > 0:
        return active_interval_seconds
    if int(last_cycle.get("unseen", 0)) == 0:
        return idle_interval_seconds
    return active_interval_seconds


def _distance_to_similarity(distance_value: Any) -> float | None:
    try:
        distance = float(distance_value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, 1.0 - distance))


def _build_vector_query_hints(
    *,
    vector_store: VectorStore,
    candidates: list[Any],
    embeddings_by_message_id: dict[str, list[float]],
    embeddings_cfg: dict[str, Any],
) -> dict[str, tuple[float, int, float]]:
    query_top_k = max(1, int(embeddings_cfg.get("query_top_k", 6)))
    min_similarity = float(embeddings_cfg.get("min_similarity_for_boost", 0.78))
    min_similarity = max(0.0, min(1.0, min_similarity))
    max_similarity_boost = float(embeddings_cfg.get("max_similarity_boost", 0.20))
    max_similarity_boost = max(0.0, min(1.0, max_similarity_boost))
    min_important_neighbors = max(
        1, int(embeddings_cfg.get("min_important_neighbors", 1))
    )

    if not candidates or not embeddings_by_message_id or max_similarity_boost == 0.0:
        return {}

    ordered_embeddings = [
        embeddings_by_message_id[item.message_id]
        for item in candidates
        if item.message_id in embeddings_by_message_id
    ]
    if len(ordered_embeddings) != len(candidates):
        return {}

    query_results = vector_store.query_similar_by_embeddings(
        ordered_embeddings,
        top_k=query_top_k + 1,
    )
    ids_rows = query_results.get("ids")
    metadata_rows = query_results.get("metadatas")
    distance_rows = query_results.get("distances")
    if (
        not isinstance(ids_rows, list)
        or not isinstance(metadata_rows, list)
        or not isinstance(distance_rows, list)
    ):
        return {}

    hints: dict[str, tuple[float, int, float]] = {}
    for index, candidate in enumerate(candidates):
        candidate_id = candidate.message_id
        neighbor_ids = (
            ids_rows[index]
            if index < len(ids_rows) and isinstance(ids_rows[index], list)
            else []
        )
        neighbors_meta = (
            metadata_rows[index]
            if index < len(metadata_rows) and isinstance(metadata_rows[index], list)
            else []
        )
        neighbors_distances = (
            distance_rows[index]
            if index < len(distance_rows) and isinstance(distance_rows[index], list)
            else []
        )
        if not neighbor_ids:
            continue

        important_hits = 0
        strongest_weight = 0.0
        best_similarity = 0.0

        for neighbor_index, neighbor_id in enumerate(neighbor_ids):
            if not isinstance(neighbor_id, str) or neighbor_id == candidate_id:
                continue

            metadata = (
                neighbors_meta[neighbor_index]
                if neighbor_index < len(neighbors_meta)
                else None
            )
            if not isinstance(metadata, dict):
                continue

            try:
                important_value = int(metadata.get("important", 0))
            except (TypeError, ValueError):
                important_value = 0
            if important_value != 1:
                continue

            similarity = _distance_to_similarity(
                neighbors_distances[neighbor_index]
                if neighbor_index < len(neighbors_distances)
                else None
            )
            if similarity is None or similarity < min_similarity:
                continue

            try:
                historical_score = float(metadata.get("score", 1.0))
            except (TypeError, ValueError):
                historical_score = 1.0
            historical_score = max(0.0, min(1.0, historical_score))

            important_hits += 1
            best_similarity = max(best_similarity, similarity)
            strongest_weight = max(
                strongest_weight, similarity * max(0.25, historical_score)
            )

        if important_hits < min_important_neighbors or strongest_weight <= 0:
            continue

        boost = min(max_similarity_boost, strongest_weight * max_similarity_boost)
        if boost <= 0:
            continue

        hints[candidate_id] = (boost, important_hits, best_similarity)

    return hints


def _process_bot_commands(
    *,
    token: str,
    config: dict[str, Any],
    store: StateStore,
    expected_chat_id: int,
    offset: int | None,
    last_cycle: dict[str, int] | None,
) -> tuple[int | None, bool]:
    try:
        updates: list[Update] = fetch_updates(
            token, offset=offset, limit=20, poll_timeout_seconds=2
        )
    except Exception as exc:
        logging.warning("Telegram update polling failed (will retry): %s", exc)
        return offset, False
    if not updates:
        return offset, False

    next_offset = offset
    should_run = False

    for update in updates:
        update_id = update.update_id
        if isinstance(update_id, int):
            candidate_offset = update_id + 1
            next_offset = (
                candidate_offset
                if next_offset is None
                else max(next_offset, candidate_offset)
            )

        callback_query = update.callback_query
        if callback_query is not None:
            _handle_callback_query(
                token=token,
                config=config,
                store=store,
                expected_chat_id=expected_chat_id,
                callback_query=callback_query,
            )
            continue

        message = update.message
        if message is None:
            continue

        chat = message.chat
        chat_id = chat.id
        if not isinstance(chat_id, int) or chat_id != expected_chat_id:
            continue

        text = message.text
        if not isinstance(text, str) or not text.startswith("/"):
            continue

        command = _normalize_command(text)
        logging.debug("Received Telegram command: %s", command)

        if command in {"/start", "/help"}:
            send_text_message(token, expected_chat_id, _help_text())
            continue

        if command == "/status":
            send_text_message(
                token, expected_chat_id, _format_status(config, store, last_cycle)
            )
            continue

        if command == "/signals":
            send_text_message(
                token,
                expected_chat_id,
                _format_recent_signals(store.recent_signal_events(limit=5)),
            )
            continue

        if command == "/ask":
            _handle_ask_command(
                token=token,
                expected_chat_id=expected_chat_id,
                text=text,
                config=config,
            )
            continue

        if command == "/watchfor":
            send_text_message(token, expected_chat_id, _handle_watch_for(text, store))
            continue

        if command == "/watchlist":
            send_text_message(token, expected_chat_id, _format_watch_rules(store))
            continue

        if command == "/unwatch":
            rule_id = _parse_unwatch_command(text)
            if rule_id is None:
                send_text_message(token, expected_chat_id, "Usage: /unwatch <rule_id>")
                continue
            deleted = store.delete_watch_rule(rule_id)
            send_text_message(
                token,
                expected_chat_id,
                ("Watch rule deleted." if deleted else "Watch rule not found."),
            )
            continue

        if command == "/run":
            should_run = True
            send_text_message(
                token, expected_chat_id, "Running an immediate poll cycle now."
            )
            continue

        send_text_message(
            token,
            expected_chat_id,
            "Unknown command. Use /help to see supported commands.",
        )

    return next_offset, should_run


def poll_once(config: dict, store: StateStore, telegram_token: str) -> dict[str, int]:
    return _poll_once_impl(config, store, telegram_token)


def run_daemon(debug: bool = False) -> None:
    config = load_config()
    _setup_logging(
        config["log"].get("level", "INFO"),
        debug=debug,
        log_file=config["log"].get("file"),
        http_debug=bool(config["log"].get("http_debug", False)),
    )
    logging.debug("Loaded config sections: %s", ", ".join(sorted(config.keys())))

    store = StateStore()
    store.initialize()
    telegram_token = get_bot_token()
    logging.debug("Telegram token loaded from secrets store.")
    try:
        prepare_polling_mode(telegram_token, drop_pending_updates=False)
        logging.debug("Telegram polling mode prepared (webhook disabled).")
    except Exception:
        logging.warning("Could not prepare Telegram polling mode.", exc_info=True)
    try:
        configure_bot_commands(telegram_token)
        logging.debug("Telegram bot commands configured.")
    except Exception:
        logging.warning(
            "Could not configure Telegram bot commands via aiogram.", exc_info=True
        )

    stop = {"value": False}

    def _handle_stop(signum, _frame):
        logging.info("Received signal %s, shutting down.", signum)
        stop["value"] = True

    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    active_interval_seconds = int(config["gmail"]["poll_interval_seconds"])
    idle_interval_seconds = int(
        config["gmail"].get("idle_poll_interval_seconds", active_interval_seconds)
    )
    chat_id = int(config["telegram"]["chat_id"])
    logging.info(
        "forgetMail daemon started. active_poll_interval=%ss idle_poll_interval=%ss debug=%s",
        active_interval_seconds,
        idle_interval_seconds,
        debug,
    )
    cycle = 0
    update_offset: int | None = None
    last_cycle: dict[str, int] | None = None
    try:
        while not stop["value"]:
            try:
                update_offset, should_run = _process_bot_commands(
                    token=telegram_token,
                    config=config,
                    store=store,
                    expected_chat_id=chat_id,
                    offset=update_offset,
                    last_cycle=last_cycle,
                )
            except Exception:
                logging.exception("Failed while processing Telegram bot commands")
                should_run = False

            if should_run:
                logging.info("Immediate poll requested by Telegram command.")
                try:
                    last_cycle = poll_once(config, store, telegram_token)
                    send_text_message(
                        telegram_token,
                        chat_id,
                        (
                            "Immediate cycle complete: "
                            f"fetched={last_cycle['fetched']} unseen={last_cycle['unseen']} "
                            f"classified={last_cycle['classified']} "
                            f"boosted={last_cycle['boosted']} "
                            f"signals={last_cycle['signals']} sent={last_cycle['sent']}"
                        ),
                    )
                except Exception:
                    logging.exception("Immediate poll failed")
                    try:
                        send_text_message(
                            telegram_token,
                            chat_id,
                            "Immediate poll failed. Check daemon logs.",
                        )
                    except Exception:
                        logging.exception(
                            "Failed to notify Telegram about immediate poll failure"
                        )

            cycle += 1
            logging.debug("Starting poll cycle #%s", cycle)
            try:
                last_cycle = poll_once(config, store, telegram_token)
            except Exception:
                logging.exception("Poll cycle failed")
            if stop["value"]:
                break

            interval_seconds = _select_poll_interval_seconds(
                active_interval_seconds=active_interval_seconds,
                idle_interval_seconds=idle_interval_seconds,
                last_cycle=last_cycle,
            )
            logging.debug("Next poll interval seconds=%s", interval_seconds)

            # Keep Telegram command latency low by polling commands frequently between mail cycles.
            next_poll_at = time.monotonic() + interval_seconds
            while not stop["value"]:
                remaining = next_poll_at - time.monotonic()
                if remaining <= 0:
                    break

                try:
                    update_offset, should_run = _process_bot_commands(
                        token=telegram_token,
                        config=config,
                        store=store,
                        expected_chat_id=chat_id,
                        offset=update_offset,
                        last_cycle=last_cycle,
                    )
                except Exception:
                    logging.exception("Failed while processing Telegram bot commands")
                    should_run = False

                if should_run:
                    logging.info("Immediate poll requested by Telegram command.")
                    try:
                        last_cycle = poll_once(config, store, telegram_token)
                        send_text_message(
                            telegram_token,
                            chat_id,
                            (
                                "Immediate cycle complete: "
                                f"fetched={last_cycle['fetched']} unseen={last_cycle['unseen']} "
                                f"classified={last_cycle['classified']} "
                                f"boosted={last_cycle['boosted']} "
                                f"signals={last_cycle['signals']} sent={last_cycle['sent']}"
                            ),
                        )
                    except Exception:
                        logging.exception("Immediate poll failed")
                        try:
                            send_text_message(
                                telegram_token,
                                chat_id,
                                "Immediate poll failed. Check daemon logs.",
                            )
                        except Exception:
                            logging.exception(
                                "Failed to notify Telegram about immediate poll failure"
                            )
                    interval_seconds = _select_poll_interval_seconds(
                        active_interval_seconds=active_interval_seconds,
                        idle_interval_seconds=idle_interval_seconds,
                        last_cycle=last_cycle,
                    )
                    logging.debug("Next poll interval seconds=%s", interval_seconds)
                    next_poll_at = time.monotonic() + interval_seconds

                sleep_for = min(2.0, max(0.1, next_poll_at - time.monotonic()))
                time.sleep(sleep_for)
    finally:
        shutdown_client()
