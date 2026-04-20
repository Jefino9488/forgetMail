from __future__ import annotations

import logging

from forgetmail.notifier import send_text_message, send_text_message_with_url_button
from forgetmail.store import StateStore

from .common import _cache_key_for


def _send_text_message(store: StateStore, token: str, chat_id: int, text: str) -> None:
    pending_alert = store.get_cache_value(_cache_key_for("pending_telegram_alert"))
    if pending_alert:
        try:
            send_text_message(token, chat_id, pending_alert)
            store.delete_cache_value(_cache_key_for("pending_telegram_alert"))
        except Exception:
            logging.warning("Failed to flush pending Telegram alert.", exc_info=True)
    send_text_message(token, chat_id, text)


def _send_text_message_with_url_button(
    store: StateStore,
    token: str,
    chat_id: int,
    text: str,
    *,
    button_text: str,
    url: str,
) -> None:
    pending_alert = store.get_cache_value(_cache_key_for("pending_telegram_alert"))
    if pending_alert:
        try:
            send_text_message(token, chat_id, pending_alert)
            store.delete_cache_value(_cache_key_for("pending_telegram_alert"))
        except Exception:
            logging.warning("Failed to flush pending Telegram alert.", exc_info=True)
    send_text_message_with_url_button(
        token,
        chat_id,
        text,
        button_text=button_text,
        url=url,
    )


def _queue_telegram_alert(store: StateStore, text: str) -> None:
    store.set_cache_value(_cache_key_for("pending_telegram_alert"), text)
