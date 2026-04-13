import logging
import signal
import time
from typing import Any

from forgetmail.auth.telegram import get_bot_token
from forgetmail.classifier import classify_messages
from forgetmail.config import load_config
from forgetmail.notifier import (
    SignalNotification,
    configure_bot_commands,
    fetch_updates,
    send_signal_notifications,
    send_text_message,
)
from forgetmail.poller import fetch_recent_unread_messages
from forgetmail.store import StateStore


def _setup_logging(level_name: str, debug: bool = False) -> None:
    level = logging.DEBUG if debug else getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")


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
        f"- lookback_days: {gmail_cfg['lookback_days']}",
        f"- max_messages_per_poll: {gmail_cfg['max_messages_per_poll']}",
        f"- llm_provider: {llm_cfg['provider']}",
        f"- llm_model: {llm_cfg['model']}",
        f"- importance_threshold: {llm_cfg['importance_threshold']}",
        f"- seen_messages: {stats['seen_messages']}",
        f"- signal_events: {stats['signal_events']}",
    ]

    if last_cycle:
        lines.append(
            (
                "- last_cycle: "
                f"fetched={last_cycle['fetched']} unseen={last_cycle['unseen']} "
                f"signals={last_cycle['signals']} sent={last_cycle['sent']} "
                f"marked_seen={last_cycle['marked_seen']}"
            )
        )

    return "\n".join(lines)


def _normalize_command(text: str) -> str:
    head = text.strip().split(maxsplit=1)[0].lower()
    return head.split("@", maxsplit=1)[0]


def _process_bot_commands(
    *,
    token: str,
    config: dict[str, Any],
    store: StateStore,
    expected_chat_id: int,
    offset: int | None,
    last_cycle: dict[str, int] | None,
) -> tuple[int | None, bool]:
    updates = fetch_updates(token, offset=offset, limit=20)
    if not updates:
        return offset, False

    next_offset = offset
    should_run = False

    for update in updates:
        update_id = update.get("update_id")
        if isinstance(update_id, int):
            candidate_offset = update_id + 1
            next_offset = candidate_offset if next_offset is None else max(next_offset, candidate_offset)

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

    messages = fetch_recent_unread_messages(
        lookback_days=int(gmail_cfg["lookback_days"]),
        max_messages=int(gmail_cfg["max_messages_per_poll"]),
    )
    logging.debug("Fetched unread candidates=%s", len(messages))
    if not messages:
        logging.info("No unread messages found in lookback window.")
        return {
            "fetched": 0,
            "unseen": 0,
            "signals": 0,
            "sent": 0,
            "marked_seen": 0,
        }

    unseen = store.unseen_ids([item.message_id for item in messages])
    candidates = [item for item in messages if item.message_id in unseen]
    logging.debug("Dedupe result: unseen=%s", len(candidates))
    if not candidates:
        logging.info("No new unread messages after dedupe.")
        return {
            "fetched": len(messages),
            "unseen": 0,
            "signals": 0,
            "sent": 0,
            "marked_seen": 0,
        }

    classifications = classify_messages(candidates, llm_cfg)
    logging.debug("Classifier returned rows=%s", len(classifications))
    signals = _build_signals(candidates, classifications, threshold)
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
    non_important_ids = set(all_by_id.keys()) - important_ids
    mark_ids = set(non_important_ids) | sent_ids

    rows_to_mark = [(message_id, all_by_id[message_id].thread_id) for message_id in mark_ids]
    store.mark_seen(rows_to_mark)
    logging.debug("Marked seen message_ids=%s", len(rows_to_mark))

    logging.info(
        "Cycle complete: fetched=%s unseen=%s signals=%s sent=%s marked_seen=%s",
        len(messages),
        len(candidates),
        len(signals),
        len(sent_ids),
        len(rows_to_mark),
    )
    return {
        "fetched": len(messages),
        "unseen": len(candidates),
        "signals": len(signals),
        "sent": len(sent_ids),
        "marked_seen": len(rows_to_mark),
    }


def run_daemon(debug: bool = False) -> None:
    config = load_config()
    _setup_logging(config["log"].get("level", "INFO"), debug=debug)
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

    interval = int(config["gmail"]["poll_interval_seconds"])
    chat_id = int(config["telegram"]["chat_id"])
    logging.info("forgetMail daemon started. Poll interval=%ss debug=%s", interval, debug)
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
        logging.debug("Sleeping for %ss before next cycle", interval)
        time.sleep(interval)
