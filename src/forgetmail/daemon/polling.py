from __future__ import annotations

import logging
from email.utils import parseaddr
from typing import Any

from forgetmail.classifier import LLMError, classify_messages
from forgetmail.embedding_client import (
    EmbeddingClient,
    EmbeddingError,
    candidate_to_embedding_text,
)
from forgetmail.notifier import SignalNotification, send_signal_notifications
from forgetmail.poller import (
    fetch_message_candidates,
    list_recent_unread_message_ids,
    apply_message_label_changes,
    mark_messages_read,
)
from forgetmail.store import StateStore
from forgetmail.vector_store import VectorStore, VectorStoreError

from .callbacks import _corrections_vector_store_from_config
from .common import _distance_to_similarity, _looks_like_newsletter

OMITTED_REASON = "Classifier omitted this message"


def _normalize_sender_email(sender: str) -> str:
    _display_name, email_address = parseaddr(sender)
    normalized = email_address.strip().lower()
    if normalized:
        return normalized
    return sender.strip().lower()


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
    min_important_neighbors = max(1, int(embeddings_cfg.get("min_important_neighbors", 1)))

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
            ids_rows[index] if index < len(ids_rows) and isinstance(ids_rows[index], list) else []
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
                neighbors_meta[neighbor_index] if neighbor_index < len(neighbors_meta) else None
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
            strongest_weight = max(strongest_weight, similarity * max(0.25, historical_score))

        if important_hits < min_important_neighbors or strongest_weight <= 0:
            continue

        boost = min(max_similarity_boost, strongest_weight * max_similarity_boost)
        if boost <= 0:
            continue

        hints[candidate_id] = (boost, important_hits, best_similarity)

    return hints


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

    results = correction_store.query_similar_by_embeddings(ordered_embeddings, top_k=query_top_k)
    ids_rows = results.get("ids")
    metadata_rows = results.get("metadatas")
    documents_rows = results.get("documents")
    distance_rows = results.get("distances")
    if not isinstance(ids_rows, list) or not isinstance(metadata_rows, list):
        return []

    by_correction_id: dict[str, tuple[float, dict[str, Any]]] = {}
    for index in range(len(candidates)):
        row_ids = (
            ids_rows[index] if index < len(ids_rows) and isinstance(ids_rows[index], list) else []
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
                str(metadata.get("original_reason", "user correction")).strip() or "user correction"
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

    sorted_examples = sorted(by_correction_id.values(), key=lambda item: item[0], reverse=True)
    return [item[1] for item in sorted_examples[:max_examples]]


def poll_once(config: dict, store: StateStore, telegram_token: str) -> dict[str, int]:
    gmail_cfg = config["gmail"]
    llm_cfg = config["llm"]
    embeddings_cfg = config.get("embeddings", {})
    threshold = float(llm_cfg.get("importance_threshold", 0.65))
    auto_label_enabled = bool(gmail_cfg.get("auto_label_enabled", True))
    archive_noise = bool(gmail_cfg.get("archive_noise", False))
    signal_label_name = (
        str(gmail_cfg.get("signal_label", "forgetMail/signal")).strip() or "forgetMail/signal"
    )
    noise_label_name = (
        str(gmail_cfg.get("noise_label", "forgetMail/noise")).strip() or "forgetMail/noise"
    )
    logging.debug(
        "Poll settings: lookback_days=%s max_messages_per_poll=%s threshold=%.2f model=%s provider=%s",
        gmail_cfg.get("lookback_days"),
        gmail_cfg.get("max_messages_per_poll"),
        threshold,
        llm_cfg.get("model"),
        llm_cfg.get("provider"),
    )

    message_ids = list_recent_unread_message_ids(
        lookback_days=int(gmail_cfg["lookback_days"]),
        max_messages=int(gmail_cfg["max_messages_per_poll"]),
    )
    logging.debug("Fetched unread ids=%s", len(message_ids))
    if not message_ids:
        logging.info("No unread messages found in lookback window.")
        return {
            "fetched": 0,
            "unseen": 0,
            "classified": 0,
            "boosted": 0,
            "vector_boosted": 0,
            "signals": 0,
            "sent": 0,
            "gmail_marked_read": 0,
            "marked_seen": 0,
            "omitted_for_retry": 0,
            "llm_failed": 0,
        }

    unseen = store.unseen_ids(message_ids)
    unseen_ids = [item for item in message_ids if item in unseen]
    logging.debug("Dedupe result: unseen=%s", len(unseen_ids))
    if not unseen_ids:
        logging.info("No new unread messages after dedupe.")
        return {
            "fetched": len(message_ids),
            "unseen": 0,
            "classified": 0,
            "boosted": 0,
            "vector_boosted": 0,
            "signals": 0,
            "sent": 0,
            "gmail_marked_read": 0,
            "marked_seen": 0,
            "omitted_for_retry": 0,
            "llm_failed": 0,
        }

    candidates = fetch_message_candidates(unseen_ids)
    logging.debug("Fetched metadata for unseen candidates=%s", len(candidates))
    if not candidates:
        logging.info("No candidate metadata fetched for unseen message ids.")
        return {
            "fetched": len(message_ids),
            "unseen": len(unseen_ids),
            "classified": 0,
            "boosted": 0,
            "vector_boosted": 0,
            "signals": 0,
            "sent": 0,
            "gmail_marked_read": 0,
            "marked_seen": 0,
            "omitted_for_retry": 0,
            "llm_failed": 0,
        }

    vector_store: VectorStore | None = None
    embeddings_by_message_id: dict[str, list[float]] = {}
    embeddings_enabled = bool(embeddings_cfg.get("enabled", False))
    vector_upsert_enabled = bool(embeddings_cfg.get("enable_vector_upsert", True))
    if embeddings_enabled and vector_upsert_enabled:
        try:
            embedding_client = EmbeddingClient.from_config(embeddings_cfg)
            vector_store = VectorStore.from_config(embeddings_cfg)
            embedding_texts = [candidate_to_embedding_text(item) for item in candidates]
            embeddings = embedding_client.embed_texts(embedding_texts)
            embeddings_by_message_id = {
                item.message_id: vector
                for item, vector in zip(candidates, embeddings, strict=False)
            }
            upserted = vector_store.upsert_email_candidates(candidates, embeddings)
            logging.debug("Vector upsert completed rows=%s", upserted)
        except (EmbeddingError, VectorStoreError, Exception) as exc:
            logging.warning(
                "Embedding/vector upsert failed; continuing without vector updates: %s",
                exc,
            )
            vector_store = None

    vector_query_enabled = bool(embeddings_cfg.get("enable_vector_query", False))
    vector_query_hints: dict[str, tuple[float, int, float]] = {}
    if vector_store is not None and vector_query_enabled and embeddings_by_message_id:
        try:
            vector_query_hints = _build_vector_query_hints(
                vector_store=vector_store,
                candidates=candidates,
                embeddings_by_message_id=embeddings_by_message_id,
                embeddings_cfg=embeddings_cfg,
            )
            logging.debug("Vector query hints generated rows=%s", len(vector_query_hints))
        except Exception as exc:
            logging.warning(
                "Vector query failed; continuing without retrieval boosts: %s",
                exc,
            )

    correction_few_shot_examples: list[dict[str, Any]] = []
    if embeddings_by_message_id and bool(embeddings_cfg.get("enable_corrections", True)):
        try:
            correction_store = _corrections_vector_store_from_config(embeddings_cfg)
            correction_few_shot_examples = _build_correction_few_shot_examples(
                correction_store=correction_store,
                candidates=candidates,
                embeddings_by_message_id=embeddings_by_message_id,
                embeddings_cfg=embeddings_cfg,
                llm_cfg=llm_cfg,
            )
            logging.debug(
                "Correction few-shot examples selected=%s",
                len(correction_few_shot_examples),
            )
        except Exception as exc:
            logging.warning(
                "Correction retrieval failed; continuing without few-shot examples: %s",
                exc,
            )

    try:
        classifications = classify_messages(
            candidates,
            llm_cfg,
            few_shot_examples=correction_few_shot_examples,
        )
    except LLMError as exc:
        logging.warning("Skipping cycle notifications due to LLM classification failure: %s", exc)
        return {
            "fetched": len(message_ids),
            "unseen": len(candidates),
            "classified": 0,
            "boosted": 0,
            "vector_boosted": 0,
            "few_shot_examples": len(correction_few_shot_examples),
            "signals": 0,
            "sent": 0,
            "gmail_marked_read": 0,
            "marked_seen": 0,
            "omitted_for_retry": 0,
            "llm_failed": 1,
        }

    logging.debug("Classifier returned rows=%s", len(classifications))
    class_map = {item.message_id: item for item in classifications}
    muted_threads = store.muted_threads([item.thread_id for item in candidates])
    muted_messages = store.muted_messages([item.message_id for item in candidates])
    vip_sender_emails = store.vip_senders(
        [_normalize_sender_email(item.sender) for item in candidates]
    )

    provider_name = str(llm_cfg.get("provider", "unknown"))
    model_name = str(llm_cfg.get("model", "unknown"))
    classification_rows: list[tuple[str, str, str, str, int, float, str, str, str]] = []
    watch_rule_events: list[tuple[int, str, str, float]] = []
    boost_count = 0
    vector_boost_count = 0
    omitted_ids: set[str] = set()

    adjusted_by_id: dict[str, tuple[bool, float, str]] = {}
    for message in candidates:
        sender_email = _normalize_sender_email(message.sender)
        is_vip_sender = sender_email in vip_sender_emails
        result = class_map.get(message.message_id)
        if result is None:
            important = False
            score = 0.0
            reason = "Missing classification row"
        else:
            important = bool(result.important)
            score = float(result.score)
            reason = result.reason

        if reason == OMITTED_REASON:
            omitted_ids.add(message.message_id)

        if is_vip_sender:
            important = True
            score = max(score, threshold)
            reason = f"{reason} | VIP sender bypass"

        matched_rules = store.match_watch_rules(
            sender=message.sender,
            subject=message.subject,
            snippet=message.snippet,
        )
        applied_boost = 0.0
        for matched_rule in matched_rules:
            rule_boost = float(matched_rule["boost"])
            applied_boost = max(applied_boost, rule_boost)
            watch_rule_events.append(
                (
                    int(matched_rule["id"]),
                    message.message_id,
                    str(matched_rule["context"]),
                    rule_boost,
                )
            )

        adjusted_score = min(1.0, score + applied_boost)
        adjusted_reason = reason
        if applied_boost > 0:
            boost_count += 1
            adjusted_reason = f"{reason} | watch boost +{applied_boost:.2f}"
            logging.debug(
                "Watch rule boost applied message_id=%s context_hits=%s base=%.2f adjusted=%.2f",
                message.message_id,
                len(matched_rules),
                score,
                adjusted_score,
            )

        query_hint = vector_query_hints.get(message.message_id)
        if query_hint is not None:
            query_boost, important_hits, best_similarity = query_hint
            adjusted_score = min(1.0, adjusted_score + query_boost)
            if not important and adjusted_score >= max(0.50, threshold - 0.10):
                important = True
            adjusted_reason = (
                f"{adjusted_reason} | vector similar important={important_hits} "
                f"max_sim={best_similarity:.2f} boost=+{query_boost:.2f}"
            )
            vector_boost_count += 1
            logging.debug(
                "Vector query boost applied message_id=%s neighbors=%s max_sim=%.2f adjusted=%.2f",
                message.message_id,
                important_hits,
                best_similarity,
                adjusted_score,
            )

        if not is_vip_sender and message.thread_id in muted_threads:
            adjusted_score = max(0.0, adjusted_score - 1.0)
            important = False
            adjusted_reason = f"{adjusted_reason} | muted thread"
            logging.debug(
                "Muted thread suppression message_id=%s thread_id=%s adjusted_score=%.2f",
                message.message_id,
                message.thread_id,
                adjusted_score,
            )

        if not is_vip_sender and message.message_id in muted_messages:
            adjusted_score = max(0.0, adjusted_score - 1.0)
            important = False
            adjusted_reason = f"{adjusted_reason} | muted message"
            logging.debug(
                "Muted message suppression message_id=%s thread_id=%s adjusted_score=%.2f",
                message.message_id,
                message.thread_id,
                adjusted_score,
            )

        if not is_vip_sender and _looks_like_newsletter(
            message.sender, message.subject, message.snippet
        ):
            adjusted_score = min(adjusted_score, 0.15)
            important = False
            adjusted_reason = f"{adjusted_reason} | newsletter pattern"
            logging.debug(
                "Newsletter suppression message_id=%s thread_id=%s adjusted_score=%.2f",
                message.message_id,
                message.thread_id,
                adjusted_score,
            )

        adjusted_by_id[message.message_id] = (
            important,
            adjusted_score,
            adjusted_reason,
        )

        classification_rows.append(
            (
                message.message_id,
                message.thread_id,
                message.sender,
                message.subject,
                1 if important else 0,
                adjusted_score,
                adjusted_reason,
                provider_name,
                model_name,
            )
        )
        logging.debug(
            "Classified message_id=%s important=%s score=%.2f subject=%r reason=%s",
            message.message_id,
            important,
            adjusted_score,
            message.subject,
            adjusted_reason,
        )

    store.record_classification_events(classification_rows)
    store.record_watch_rule_events(watch_rule_events)
    if vector_store is not None:
        try:
            updated = vector_store.update_classification_results(classification_rows)
            logging.debug("Vector classification metadata updated rows=%s", updated)
        except Exception as exc:
            logging.warning(
                "Vector metadata update failed; continuing without vector metadata updates: %s",
                exc,
            )
    logging.debug(
        "Recorded classification rows=%s; proceeding with signal filtering",
        len(classification_rows),
    )

    if auto_label_enabled:
        signal_ids = [
            item.message_id
            for item in candidates
            if adjusted_by_id.get(item.message_id, (False, 0.0, ""))[0]
        ]
        noise_ids = [
            item.message_id
            for item in candidates
            if item.message_id not in signal_ids and item.message_id not in omitted_ids
        ]
        if signal_ids:
            try:
                updated_signal_ids = apply_message_label_changes(
                    signal_ids,
                    add_label_names=[signal_label_name],
                )
                logging.debug("Applied signal label to messages=%s", len(updated_signal_ids))
            except Exception as exc:
                logging.warning("Signal label update failed; continuing: %s", exc)
        if noise_ids:
            try:
                updated_noise_ids = apply_message_label_changes(
                    noise_ids,
                    add_label_names=[noise_label_name],
                    remove_label_names=["INBOX"] if archive_noise else None,
                )
                logging.debug(
                    "Applied noise label to messages=%s archive_enabled=%s",
                    len(updated_noise_ids),
                    archive_noise,
                )
            except Exception as exc:
                logging.warning("Noise label/archive update failed; continuing: %s", exc)

    adjusted_signals: list[SignalNotification] = []
    for message in candidates:
        adjusted = adjusted_by_id.get(message.message_id)
        if adjusted is None:
            continue
        adjusted_important, adjusted_score, adjusted_reason = adjusted
        if adjusted_important and adjusted_score >= threshold:
            adjusted_signals.append(
                SignalNotification(
                    message_id=message.message_id,
                    thread_id=message.thread_id,
                    sender=message.sender,
                    subject=message.subject,
                    reason=adjusted_reason,
                    score=adjusted_score,
                )
            )

    signals = adjusted_signals
    logging.debug("Signal candidates=%s", len(signals))
    chat_id = int(config["telegram"]["chat_id"])

    sent_ids: set[str] = set()
    if signals:
        sent_ids = send_signal_notifications(telegram_token, chat_id, signals)
        signal_rows = [
            (
                item.message_id,
                item.thread_id,
                item.sender,
                item.subject,
                item.reason,
                item.score,
            )
            for item in signals
            if item.message_id in sent_ids
        ]
        store.record_signal_events(signal_rows)
    logging.debug("Telegram sent notifications=%s", len(sent_ids))

    all_by_id = {item.message_id: item for item in candidates}
    important_ids = {item.message_id for item in signals}
    non_important_ids = (set(all_by_id.keys()) - important_ids) - omitted_ids
    read_marked_ids = mark_messages_read(sorted(non_important_ids))
    logging.debug("Marked read in Gmail message_ids=%s", len(read_marked_ids))
    mark_ids = set(read_marked_ids) | sent_ids

    rows_to_mark = [(message_id, all_by_id[message_id].thread_id) for message_id in mark_ids]
    store.mark_seen(rows_to_mark)
    logging.debug("Marked seen message_ids=%s", len(rows_to_mark))

    logging.info(
        "Cycle complete: fetched=%s unseen=%s classified=%s boosted=%s vector_boosted=%s few_shot_examples=%s signals=%s sent=%s gmail_marked_read=%s omitted_for_retry=%s marked_seen=%s llm_failed=0",
        len(message_ids),
        len(candidates),
        len(classification_rows),
        boost_count,
        vector_boost_count,
        len(correction_few_shot_examples),
        len(signals),
        len(sent_ids),
        len(read_marked_ids),
        len(omitted_ids),
        len(rows_to_mark),
    )
    return {
        "fetched": len(message_ids),
        "unseen": len(candidates),
        "classified": len(classification_rows),
        "boosted": boost_count,
        "vector_boosted": vector_boost_count,
        "few_shot_examples": len(correction_few_shot_examples),
        "signals": len(signals),
        "sent": len(sent_ids),
        "gmail_marked_read": len(read_marked_ids),
        "gmail_labelled": len(candidates) if auto_label_enabled else 0,
        "gmail_archived": (len(candidates) if auto_label_enabled and archive_noise else 0),
        "marked_seen": len(rows_to_mark),
        "omitted_for_retry": len(omitted_ids),
        "llm_failed": 0,
    }
