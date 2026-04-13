from __future__ import annotations

import httpx

from forgetmail.secrets import get_secret, set_secret

TELEGRAM_BOT_TOKEN_KEY = "telegram_bot_token"


def validate_token(token: str) -> dict:
    response = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    response.raise_for_status()

    data = response.json()
    if not data.get("ok"):
        raise ValueError(f"Telegram rejected token: {data}")

    return data["result"]


def cache_bot_token(token: str) -> None:
    if not set_secret(TELEGRAM_BOT_TOKEN_KEY, token):
        raise RuntimeError(
            "Could not store Telegram token in keyring. "
            "Set FORGETMAIL_TELEGRAM_BOT_TOKEN as an environment variable."
        )


def get_bot_token() -> str:
    token = get_secret(TELEGRAM_BOT_TOKEN_KEY)
    if not token:
        raise RuntimeError("Telegram bot token is missing. Run forgetMail --onboard.")
    return token


def detect_chat_id(token: str) -> int:
    response = httpx.get(
        f"https://api.telegram.org/bot{token}/getUpdates",
        params={"limit": 5, "timeout": 0},
        timeout=15,
    )
    response.raise_for_status()

    updates = response.json().get("result", [])
    for update in reversed(updates):
        message = update.get("message")
        if message and message.get("chat", {}).get("id"):
            return int(message["chat"]["id"])

    raise RuntimeError(
        "No Telegram messages found for this bot. Send any message to your bot and run --onboard again."
    )
