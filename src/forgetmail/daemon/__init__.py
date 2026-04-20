from __future__ import annotations

import logging
import signal
import time
from datetime import datetime, timezone
from typing import Any

try:
    from aiogram.types import Update
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    Update = Any

from forgetmail.auth.telegram import get_bot_token
from forgetmail.config import load_config
from forgetmail.notifier import (
    configure_bot_commands,
    fetch_updates,
    prepare_polling_mode,
    shutdown_client,
)
from forgetmail.store import StateStore

from .ask import _handle_ask_command
from .callbacks import _handle_callback_query
from .commands import (
    _format_recent_signals,
    _format_status,
    _format_watch_rules,
    _handle_set_command,
    _handle_vip_command,
    _handle_watch_for,
    _help_text,
    _normalize_command,
    _parse_unwatch_command,
)
from .common import (
    _cache_key_for,
    _credential_refresh_warning_key,
    _heartbeat_due_now,
    _select_poll_interval_seconds,
)
from .logging_utils import _setup_logging
from .polling import poll_once as _poll_once_impl
from .telegram_io import _queue_telegram_alert, _send_text_message


def _refresh_credentials_with_warning(
    *,
    store: StateStore,
    allow_reauth: bool = False,
    refresh_timeout_seconds: int = 12,
) -> bool:
    from forgetmail.auth.google import get_credentials

    try:
        get_credentials(allow_reauth=allow_reauth, refresh_timeout_seconds=refresh_timeout_seconds)
        store.delete_cache_value(_cache_key_for("credential_refresh_failure"))
        return True
    except Exception as exc:
        detail = str(exc).strip() or exc.__class__.__name__
        detail_lower = detail.lower()
        if (
            "invalid_grant" in detail_lower
            or "revoked" in detail_lower
            or "expired" in detail_lower
        ):
            warning_key = _credential_refresh_warning_key(detail)
            if store.get_cache_value(warning_key) is None:
                store.set_cache_value(warning_key, datetime.now(timezone.utc).isoformat())
                store.set_cache_value(_cache_key_for("credential_refresh_failure"), detail)
            raise RuntimeError(
                "Google credentials could not be refreshed. Re-run forgetMail --onboard to re-authenticate."
            ) from exc
        raise


def _maybe_send_heartbeat(
    *,
    config: dict[str, Any],
    store: StateStore,
    token: str,
    chat_id: int,
    last_cycle: dict[str, int] | None,
) -> bool:
    health_cfg = config.get("health", {})
    if not bool(health_cfg.get("heartbeat_enabled", True)):
        return False

    last_sent = store.get_cache_value(_cache_key_for("heartbeat_last_sent_date"))
    now = datetime.now().astimezone()
    if not _heartbeat_due_now(now, str(health_cfg.get("heartbeat_local_time", "09:00")), last_sent):
        return False

    stats = store.stats()
    heartbeat_lines = [
        "forgetMail heartbeat: alive",
        f"- time: {now.isoformat(timespec='seconds')}",
        f"- seen_messages: {stats['seen_messages']}",
        f"- signal_events: {stats['signal_events']}",
        f"- vip_senders: {stats.get('vip_senders', 0)}",
    ]
    if last_cycle:
        heartbeat_lines.append(
            (
                "- last_cycle: "
                f"fetched={last_cycle['fetched']} unseen={last_cycle['unseen']} "
                f"signals={last_cycle['signals']} sent={last_cycle['sent']} "
                f"llm_failed={last_cycle['llm_failed']}"
            )
        )

    _send_text_message(store, token, chat_id, "\n".join(heartbeat_lines))
    store.set_cache_value(_cache_key_for("heartbeat_last_sent_date"), now.date().isoformat())
    return True


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
                candidate_offset if next_offset is None else max(next_offset, candidate_offset)
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
            _send_text_message(store, token, expected_chat_id, _help_text())
            continue
        if command == "/status":
            _send_text_message(
                store,
                token,
                expected_chat_id,
                _format_status(config, store, last_cycle),
            )
            continue
        if command == "/signals":
            _send_text_message(
                store,
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
                store=store,
            )
            continue
        if command == "/watchfor":
            _send_text_message(store, token, expected_chat_id, _handle_watch_for(text, store))
            continue
        if command == "/watchlist":
            _send_text_message(store, token, expected_chat_id, _format_watch_rules(store))
            continue
        if command == "/unwatch":
            rule_id = _parse_unwatch_command(text)
            if rule_id is None:
                _send_text_message(store, token, expected_chat_id, "Usage: /unwatch <rule_id>")
                continue
            deleted = store.delete_watch_rule(rule_id)
            _send_text_message(
                store,
                token,
                expected_chat_id,
                "Watch rule deleted." if deleted else "Watch rule not found.",
            )
            continue
        if command == "/set":
            _send_text_message(store, token, expected_chat_id, _handle_set_command(text, config))
            continue
        if command == "/vip":
            _send_text_message(store, token, expected_chat_id, _handle_vip_command(text, store))
            continue
        if command == "/run":
            should_run = True
            _send_text_message(
                store, token, expected_chat_id, "Running an immediate poll cycle now."
            )
            continue

        _send_text_message(
            store,
            token,
            expected_chat_id,
            "Unknown command. Use /help to see supported commands.",
        )

    return next_offset, should_run


def poll_once(config: dict, store: StateStore, telegram_token: str) -> dict[str, int]:
    return _poll_once_impl(config, store, telegram_token)


def _run_immediate_cycle(
    *,
    config: dict[str, Any],
    store: StateStore,
    telegram_token: str,
    chat_id: int,
) -> tuple[dict[str, int] | None, bool]:
    refresh_ok = True
    try:
        _refresh_credentials_with_warning(store=store, allow_reauth=False)
    except RuntimeError as exc:
        refresh_ok = False
        logging.warning("Credential refresh failed: %s", exc)
        try:
            _send_text_message(store, telegram_token, chat_id, str(exc))
        except Exception:
            logging.warning("Could not deliver credential refresh warning.")
            _queue_telegram_alert(store, str(exc))

    if not refresh_ok:
        return None, False

    try:
        last_cycle = poll_once(config, store, telegram_token)
        _send_text_message(
            store,
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
        return last_cycle, True
    except Exception:
        logging.exception("Immediate poll failed")
        try:
            _send_text_message(
                store,
                telegram_token,
                chat_id,
                "Immediate poll failed. Check daemon logs.",
            )
        except Exception:
            logging.exception("Failed to notify Telegram about immediate poll failure")
        return None, False


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
        logging.warning("Could not configure Telegram bot commands via aiogram.", exc_info=True)

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
    health_cfg = config.get("health", {})
    watchdog_failure_threshold = max(1, int(health_cfg.get("watchdog_failure_threshold", 3)))
    watchdog_retry_base_seconds = max(1, int(health_cfg.get("watchdog_retry_base_seconds", 2)))
    watchdog_retry_max_seconds = max(1, int(health_cfg.get("watchdog_retry_max_seconds", 30)))
    chat_id = int(config["telegram"]["chat_id"])

    logging.info(
        "forgetMail daemon started. active_poll_interval=%ss idle_poll_interval=%ss debug=%s",
        active_interval_seconds,
        idle_interval_seconds,
        debug,
    )

    update_offset: int | None = None
    last_cycle: dict[str, int] | None = None
    consecutive_watchdog_failures = 0
    last_failure_detail = ""

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
                consecutive_watchdog_failures += 1
                last_failure_detail = "telegram update polling failed"

            try:
                _maybe_send_heartbeat(
                    config=config,
                    store=store,
                    token=telegram_token,
                    chat_id=chat_id,
                    last_cycle=last_cycle,
                )
            except Exception as exc:
                logging.warning("Heartbeat delivery failed: %s", exc)
                consecutive_watchdog_failures += 1
                last_failure_detail = str(exc)

            if should_run:
                logging.info("Immediate poll requested by Telegram command.")
                immediate_cycle, immediate_ok = _run_immediate_cycle(
                    config=config,
                    store=store,
                    telegram_token=telegram_token,
                    chat_id=chat_id,
                )
                if immediate_ok and immediate_cycle is not None:
                    last_cycle = immediate_cycle
                    consecutive_watchdog_failures = 0
                    last_failure_detail = ""
                else:
                    consecutive_watchdog_failures += 1
                    last_failure_detail = "immediate poll failed"

            refresh_ok = True
            try:
                _refresh_credentials_with_warning(store=store, allow_reauth=False)
            except RuntimeError as exc:
                refresh_ok = False
                last_failure_detail = str(exc)
                consecutive_watchdog_failures += 1
                logging.warning("Credential refresh failed: %s", exc)
                try:
                    _send_text_message(store, telegram_token, chat_id, str(exc))
                except Exception:
                    logging.warning("Could not deliver credential refresh warning.")
                    _queue_telegram_alert(store, str(exc))

            if refresh_ok:
                try:
                    last_cycle = poll_once(config, store, telegram_token)
                    consecutive_watchdog_failures = 0
                    last_failure_detail = ""
                    store.delete_cache_value(_cache_key_for("watchdog_active_alert"))
                except Exception:
                    logging.exception("Poll cycle failed")
                    consecutive_watchdog_failures += 1
                    last_failure_detail = "poll cycle failed"
                    if consecutive_watchdog_failures >= watchdog_failure_threshold:
                        alert_text = (
                            "forgetMail watchdog alert: repeated failures detected\n"
                            f"- failures: {consecutive_watchdog_failures}\n"
                            f"- last_error: {last_failure_detail}\n"
                            "The daemon will keep retrying with backoff."
                        )
                        alert_key = _cache_key_for("watchdog_active_alert")
                        if store.get_cache_value(alert_key) != alert_text:
                            try:
                                _send_text_message(store, telegram_token, chat_id, alert_text)
                                store.set_cache_value(alert_key, alert_text)
                            except Exception:
                                logging.warning(
                                    "Failed to deliver watchdog alert; queueing for later."
                                )
                                _queue_telegram_alert(store, alert_text)
                                store.set_cache_value(alert_key, alert_text)

            if stop["value"]:
                break

            interval_seconds = _select_poll_interval_seconds(
                active_interval_seconds=active_interval_seconds,
                idle_interval_seconds=idle_interval_seconds,
                last_cycle=last_cycle,
            )
            if consecutive_watchdog_failures > 0:
                backoff_seconds = min(
                    watchdog_retry_max_seconds,
                    watchdog_retry_base_seconds * (2 ** (consecutive_watchdog_failures - 1)),
                )
                interval_seconds = min(interval_seconds, backoff_seconds)

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
                    immediate_cycle, immediate_ok = _run_immediate_cycle(
                        config=config,
                        store=store,
                        telegram_token=telegram_token,
                        chat_id=chat_id,
                    )
                    if immediate_ok and immediate_cycle is not None:
                        last_cycle = immediate_cycle
                        consecutive_watchdog_failures = 0
                        last_failure_detail = ""
                    else:
                        consecutive_watchdog_failures += 1
                        last_failure_detail = "immediate poll failed"

                    interval_seconds = _select_poll_interval_seconds(
                        active_interval_seconds=active_interval_seconds,
                        idle_interval_seconds=idle_interval_seconds,
                        last_cycle=last_cycle,
                    )
                    if consecutive_watchdog_failures > 0:
                        backoff_seconds = min(
                            watchdog_retry_max_seconds,
                            watchdog_retry_base_seconds
                            * (2 ** (consecutive_watchdog_failures - 1)),
                        )
                        interval_seconds = min(interval_seconds, backoff_seconds)
                    next_poll_at = time.monotonic() + interval_seconds

                sleep_for = min(2.0, max(0.1, next_poll_at - time.monotonic()))
                time.sleep(sleep_for)
    finally:
        shutdown_client()
