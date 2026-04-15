from __future__ import annotations

from forgetmail.secrets import get_secret, set_secret
from forgetmail.telegram import AiogramBotClient

TELEGRAM_BOT_TOKEN_KEY = "telegram_bot_token"


def validate_token(token: str) -> dict:
    return AiogramBotClient().validate_token(token)


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


def ensure_polling_mode(token: str, *, drop_pending_updates: bool = False) -> None:
    AiogramBotClient().prepare_polling(token, drop_pending_updates=drop_pending_updates)


def detect_chat_id(token: str) -> int:
    ensure_polling_mode(token, drop_pending_updates=False)
    return AiogramBotClient().detect_chat_id(token)
