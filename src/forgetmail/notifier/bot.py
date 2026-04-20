from __future__ import annotations

import logging

try:
    from aiogram.types import Update
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    Update = object

from forgetmail.telegram import AiogramBotClient

from .models import SignalNotification

BOT_COMMANDS: list[dict[str, str]] = [
    {"command": "help", "description": "Show available bot commands"},
    {"command": "status", "description": "Show daemon and classifier status"},
    {"command": "signals", "description": "Show recent detected important signals"},
    {"command": "ask", "description": "Ask about your inbox: /ask <question>"},
    {
        "command": "watchfor",
        "description": "Add watch context: /watchFor <context> [boost]",
    },
    {"command": "watchlist", "description": "List active watch rules"},
    {"command": "unwatch", "description": "Delete watch rule: /unwatch <id>"},
    {"command": "set", "description": "Set runtime options: /set archive on|off"},
    {"command": "vip", "description": "Manage VIP senders: /vip add|list|remove"},
    {"command": "run", "description": "Run one immediate poll cycle"},
]


def _aiogram_client() -> AiogramBotClient:
    return AiogramBotClient()


def shutdown_client() -> None:
    AiogramBotClient.close_all()


def prepare_polling_mode(token: str, *, drop_pending_updates: bool = False) -> None:
    _aiogram_client().prepare_polling(token, drop_pending_updates=drop_pending_updates)


def configure_bot_commands(token: str) -> None:
    _aiogram_client().configure_bot_commands(token, BOT_COMMANDS)


def fetch_updates(
    token: str,
    offset: int | None,
    limit: int = 20,
    poll_timeout_seconds: int = 2,
) -> list[Update]:
    return _aiogram_client().fetch_updates(
        token,
        offset=offset,
        limit=limit,
        poll_timeout_seconds=poll_timeout_seconds,
    )


def send_text_message(token: str, chat_id: int, text: str) -> None:
    _aiogram_client().send_text_message(token, chat_id, text)


def send_text_message_with_url_button(
    token: str,
    chat_id: int,
    text: str,
    *,
    button_text: str,
    url: str,
) -> None:
    _aiogram_client().send_text_message_with_url_button(
        token,
        chat_id,
        text,
        button_text=button_text,
        url=url,
    )


def answer_callback_query(token: str, callback_query_id: str, text: str) -> None:
    _aiogram_client().answer_callback_query(token, callback_query_id, text)


def send_signal_notifications(
    token: str, chat_id: int, signals: list[SignalNotification]
) -> set[str]:
    logging.debug("Notifier: sending signals=%s chat_id=%s", len(signals), chat_id)
    sent_ids = _aiogram_client().send_signal_notifications(token, chat_id, signals)

    logging.debug("Notifier: successfully sent=%s", len(sent_ids))

    return sent_ids
