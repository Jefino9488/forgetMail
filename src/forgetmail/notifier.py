from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

import httpx

BOT_COMMANDS: list[dict[str, str]] = [
    {"command": "help", "description": "Show available bot commands"},
    {"command": "status", "description": "Show daemon and classifier status"},
    {"command": "signals", "description": "Show recent detected important signals"},
    {"command": "watchfor", "description": "Add watch context: /watchFor <context> [boost]"},
    {"command": "watchlist", "description": "List active watch rules"},
    {"command": "unwatch", "description": "Delete watch rule: /unwatch <id>"},
    {"command": "run", "description": "Run one immediate poll cycle"},
]


@dataclass
class SignalNotification:
    message_id: str
    thread_id: str
    sender: str
    subject: str
    reason: str
    score: float


def _post(token: str, method: str, payload: dict[str, Any], timeout: int = 15) -> dict[str, Any]:
    response = httpx.post(
        f"https://api.telegram.org/bot{token}/{method}",
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or not data.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {data}")
    return data


def _get(token: str, method: str, params: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    response = httpx.get(
        f"https://api.telegram.org/bot{token}/{method}",
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or not data.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {data}")
    return data


def configure_bot_commands(token: str) -> None:
    _post(token, "setMyCommands", {"commands": BOT_COMMANDS}, timeout=15)


def fetch_updates(
    token: str,
    offset: int | None,
    limit: int = 20,
    poll_timeout_seconds: int = 2,
) -> list[dict[str, Any]]:
    timeout_value = max(0, int(poll_timeout_seconds))
    params: dict[str, Any] = {"limit": limit, "timeout": timeout_value}
    if offset is not None:
        params["offset"] = offset
    data = _get(token, "getUpdates", params, timeout=max(10, timeout_value + 5))
    updates = data.get("result", [])
    if not isinstance(updates, list):
        return []
    return [item for item in updates if isinstance(item, dict)]


def send_text_message(token: str, chat_id: int, text: str) -> None:
    _post(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
        },
        timeout=15,
    )


def answer_callback_query(token: str, callback_query_id: str, text: str) -> None:
    _post(
        token,
        "answerCallbackQuery",
        {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": False,
        },
        timeout=10,
    )


def _build_summary(subject: str, reason: str) -> str:
    subject_value = " ".join(subject.split())
    reason_value = " ".join(reason.split())
    summary = f"{subject_value}. {reason_value}".strip(" .")
    if len(summary) > 220:
        return summary[:217].rstrip() + "..."
    return summary


def send_signal_notifications(token: str, chat_id: int, signals: list[SignalNotification]) -> set[str]:
    sent_ids: set[str] = set()
    logging.debug("Notifier: sending signals=%s chat_id=%s", len(signals), chat_id)
    for signal in signals:
        logging.debug("Notifier: sending message_id=%s thread_id=%s", signal.message_id, signal.thread_id)
        summary = _build_summary(signal.subject, signal.reason)
        text = (
            "Important email summary\n"
            f"From: {signal.sender}\n"
            f"Summary: {summary}\n"
            f"Score: {signal.score:.2f}"
        )
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "Reply", "callback_data": f"reply:{signal.thread_id}"},
                    {"text": "Not important", "callback_data": f"notimportant:{signal.thread_id}"},
                ]
            ]
        }

        payload = _post(
            token,
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text,
                "reply_markup": reply_markup,
            },
            timeout=15,
        )
        if payload.get("ok"):
            sent_ids.add(signal.message_id)

    logging.debug("Notifier: successfully sent=%s", len(sent_ids))

    return sent_ids
