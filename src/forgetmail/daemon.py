import logging
import signal
import time
from pathlib import Path
from typing import Any

from forgetmail.auth.telegram import get_bot_token
from forgetmail.classifier import LLMError
from forgetmail.classifier import classify_messages
from forgetmail.config import load_config
from forgetmail.notifier import (
    SignalNotification,
    answer_callback_query,
    configure_bot_commands,
    fetch_updates,
    send_signal_notifications,
    send_text_message,
)
from forgetmail.poller import (
    fetch_message_candidates,
    list_recent_unread_message_ids,
    mark_messages_read,
)
from forgetmail.store import StateStore

OMITTED_REASON = "Classifier omitted this message"


def _setup_logging(
    level_name: str,
    debug: bool = False,
    log_file: str | None = None,
    http_debug: bool = False,
) -> None:
    level = logging.DEBUG if debug else getattr(logging, level_name.upper(), logging.INFO)
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


def _build_signals(messages, classifications, threshold: float) -> list[SignalNotification]:
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
                f"- {item['notified_at']} | {item['subject']} | "
                f"score={float(item['score']):.2f}"
            )
        )
    return "\n".join(lines)


def _format_status(config: dict[str, Any], store: StateStore, last_cycle: dict[str, int] | None) -> str:
    stats = store.stats()
    llm_cfg = config["llm"]
    gmail_cfg = config["gmail"]
    lines = [
        "forgetMail status:",
        f"- poll_interval_seconds: {gmail_cfg['poll_interval_seconds']}",
        f"- idle_poll_interval_seconds: {gmail_cfg.get('idle_poll_interval_seconds', gmail_cfg['poll_interval_seconds'])}",
        f"- lookback_days: {gmail_cfg['lookback_days']}",
        f"- max_messages_per_poll: {gmail_cfg['max_messages_per_poll']}",
        f"- llm_provider: {llm_cfg['provider']}",
        f"- llm_model: {llm_cfg['model']}",
        f"- importance_threshold: {llm_cfg['importance_threshold']}",
        f"- seen_messages: {stats['seen_messages']}",
        f"- signal_events: {stats['signal_events']}",
        f"- classification_events: {stats['classification_events']}",
        f"- watch_rules: {stats['watch_rules']}",
        f"- watch_rule_events: {stats['watch_rule_events']}",
        f"- muted_threads: {stats['muted_threads']}",
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
                f"- id={item['id']} context={item['context']} "
                f"boost={float(item['boost']):.2f}"
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


def _handle_callback_query(
    *,
    token: str,
    store: StateStore,
    expected_chat_id: int,
    callback_query: dict[str, Any],
) -> None:
    callback_id = callback_query.get("id")
    callback_data = callback_query.get("data")
    message = callback_query.get("message")
    if not isinstance(callback_id, str) or not callback_id:
        return
    if not isinstance(callback_data, str) or not callback_data:
        answer_callback_query(token, callback_id, "Unsupported action")
        return
    if not isinstance(message, dict):
        answer_callback_query(token, callback_id, "Unsupported action")
        return

    chat = message.get("chat")
    if not isinstance(chat, dict):
        answer_callback_query(token, callback_id, "Unsupported action")
        return

    chat_id = chat.get("id")
    if not isinstance(chat_id, int) or chat_id != expected_chat_id:
        answer_callback_query(token, callback_id, "Action denied")
        return

    if callback_data.startswith("reply:"):
        answer_callback_query(token, callback_id, "Reply workflow coming soon")
        send_text_message(token, expected_chat_id, "Reply action received. Reply workflow is coming soon.")
        return

    if callback_data.startswith("notimportant:"):
        thread_id = callback_data.split(":", maxsplit=1)[1].strip()
        if not thread_id:
            answer_callback_query(token, callback_id, "Invalid thread id")
            return
        store.mute_thread(thread_id=thread_id)
        answer_callback_query(token, callback_id, "Marked not important")
        send_text_message(
            token,
            expected_chat_id,
            "Marked thread as not important. Future notifications for this thread are suppressed.",
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
        updates = fetch_updates(token, offset=offset, limit=20, poll_timeout_seconds=2)
    except Exception as exc:
        logging.warning("Telegram getUpdates failed (will retry): %s", exc)
        return offset, False
    if not updates:
        return offset, False

    next_offset = offset
    should_run = False

    for update in updates:
        update_id = update.get("update_id")
        if isinstance(update_id, int):
            candidate_offset = update_id + 1
            next_offset = candidate_offset if next_offset is None else max(next_offset, candidate_offset)

        callback_query = update.get("callback_query")
        if isinstance(callback_query, dict):
            _handle_callback_query(
                token=token,
                store=store,
                expected_chat_id=expected_chat_id,
                callback_query=callback_query,
            )
            continue

        message = update.get("message")
        if not isinstance(message, dict):
            continue

        chat = message.get("chat")
        if not isinstance(chat, dict):
            continue

        chat_id = chat.get("id")
        if not isinstance(chat_id, int) or chat_id != expected_chat_id:
            continue

        text = message.get("text")
        if not isinstance(text, str) or not text.startswith("/"):
            continue

        command = _normalize_command(text)
        logging.debug("Received Telegram command: %s", command)

        if command in {"/start", "/help"}:
            send_text_message(token, expected_chat_id, _help_text())
            continue

        if command == "/status":
            send_text_message(token, expected_chat_id, _format_status(config, store, last_cycle))
            continue

        if command == "/signals":
            send_text_message(token, expected_chat_id, _format_recent_signals(store.recent_signal_events(limit=5)))
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
            send_text_message(token, expected_chat_id, "Running an immediate poll cycle now.")
            continue

        send_text_message(
            token,
            expected_chat_id,
            "Unknown command. Use /help to see supported commands.",
        )

    return next_offset, should_run


def poll_once(config: dict, store: StateStore, telegram_token: str) -> dict[str, int]:
    gmail_cfg = config["gmail"]
    llm_cfg = config["llm"]
    threshold = float(llm_cfg.get("importance_threshold", 0.65))
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
            "signals": 0,
            "sent": 0,
            "gmail_marked_read": 0,
            "marked_seen": 0,
            "omitted_for_retry": 0,
            "llm_failed": 0,
        }

    try:
        classifications = classify_messages(candidates, llm_cfg)
    except LLMError as exc:
        logging.warning("Skipping cycle notifications due to LLM classification failure: %s", exc)
        return {
            "fetched": len(message_ids),
            "unseen": len(candidates),
            "classified": 0,
            "boosted": 0,
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

    provider_name = str(llm_cfg.get("provider", "unknown"))
    model_name = str(llm_cfg.get("model", "unknown"))
    classification_rows: list[tuple[str, str, str, str, int, float, str, str, str]] = []
    watch_rule_events: list[tuple[int, str, str, float]] = []
    boost_count = 0
    omitted_ids: set[str] = set()

    adjusted_by_id: dict[str, tuple[bool, float, str]] = {}
    for message in candidates:
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

        if message.thread_id in muted_threads:
            adjusted_score = max(0.0, adjusted_score - 1.0)
            important = False
            adjusted_reason = f"{adjusted_reason} | muted thread"
            logging.debug(
                "Muted thread suppression message_id=%s thread_id=%s adjusted_score=%.2f",
                message.message_id,
                message.thread_id,
                adjusted_score,
            )

        if _looks_like_newsletter(message.sender, message.subject, message.snippet):
            adjusted_score = min(adjusted_score, 0.15)
            important = False
            adjusted_reason = f"{adjusted_reason} | newsletter pattern"
            logging.debug(
                "Newsletter suppression message_id=%s thread_id=%s adjusted_score=%.2f",
                message.message_id,
                message.thread_id,
                adjusted_score,
            )

        adjusted_by_id[message.message_id] = (important, adjusted_score, adjusted_reason)

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
    logging.debug("Recorded classification rows=%s; proceeding with signal filtering", len(classification_rows))

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
            (item.message_id, item.thread_id, item.sender, item.subject, item.reason, item.score)
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
        "Cycle complete: fetched=%s unseen=%s classified=%s boosted=%s signals=%s sent=%s gmail_marked_read=%s omitted_for_retry=%s marked_seen=%s llm_failed=0",
        len(message_ids),
        len(candidates),
        len(classification_rows),
        boost_count,
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
        "signals": len(signals),
        "sent": len(sent_ids),
        "gmail_marked_read": len(read_marked_ids),
        "marked_seen": len(rows_to_mark),
        "omitted_for_retry": len(omitted_ids),
        "llm_failed": 0,
    }


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
        configure_bot_commands(telegram_token)
        logging.debug("Telegram bot commands configured.")
    except Exception:
        logging.warning("Could not configure Telegram bot commands via setMyCommands.", exc_info=True)

    stop = {"value": False}

    def _handle_stop(signum, _frame):
        logging.info("Received signal %s, shutting down.", signum)
        stop["value"] = True

    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    active_interval_seconds = int(config["gmail"]["poll_interval_seconds"])
    idle_interval_seconds = int(config["gmail"].get("idle_poll_interval_seconds", active_interval_seconds))
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
                    logging.exception("Failed to notify Telegram about immediate poll failure")

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
                        logging.exception("Failed to notify Telegram about immediate poll failure")
                interval_seconds = _select_poll_interval_seconds(
                    active_interval_seconds=active_interval_seconds,
                    idle_interval_seconds=idle_interval_seconds,
                    last_cycle=last_cycle,
                )
                logging.debug("Next poll interval seconds=%s", interval_seconds)
                next_poll_at = time.monotonic() + interval_seconds

            sleep_for = min(2.0, max(0.1, next_poll_at - time.monotonic()))
            time.sleep(sleep_for)
