from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

from forgetmail.auth.google import DEFAULT_CLIENT_SECRET_PATH, get_credentials
from forgetmail.auth.telegram import (
    cache_bot_token,
    detect_chat_id,
    ensure_polling_mode,
    get_bot_token,
    validate_token,
)
from forgetmail.config import CONFIG_PATH, ensure_config_dir, load_config, save_config
from forgetmail.gmail_client import GmailClient
from forgetmail.llm import cache_llm_api_key, detect_ollama_models, validate_llm_connection


def _is_connectivity_failure(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "name or service not known",
        "gaierror",
        "dns",
        "temporary failure in name resolution",
        "connection timed out",
        "read timed out",
        "max retries exceeded",
        "connection aborted",
        "connection reset",
        "network is unreachable",
    )
    return any(marker in text for marker in markers)


def _prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a value.")


def _import_client_secret() -> Path:
    ensure_config_dir()
    target = DEFAULT_CLIENT_SECRET_PATH

    if target.exists():
        use_existing = input(f"Use existing client secret at {target}? [Y/n]: ").strip().lower()
        if use_existing in ("", "y", "yes"):
            return target

    source_input = _prompt_non_empty("Path to your client_secret.json: ")
    source = Path(source_input).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"client_secret.json not found at: {source}")

    shutil.copy2(source, target)
    try:
        os.chmod(target, 0o600)
    except OSError:
        pass
    return target


def _detect_chat_id_with_retry(token: str, attempts: int = 5, delay_seconds: int = 3) -> int:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return detect_chat_id(token)
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                print(
                    "No Telegram messages found yet. Send /start (or any message) to your bot, "
                    f"then waiting {delay_seconds}s before retry ({attempt}/{attempts - 1})..."
                )
                time.sleep(delay_seconds)
    raise RuntimeError(f"Could not detect Telegram chat_id: {last_error}")


def _onboard_llm() -> dict[str, object]:
    print("\n[3/3] LLM")
    models = detect_ollama_models()
    if models:
        print("Detected local Ollama server.")
        print(f"Available models: {', '.join(models)}")
        selected = input(f"Use local Ollama model '{models[0]}'? [Y/n]: ").strip().lower()
        if selected in ("", "y", "yes"):
            return {
                "provider": "ollama",
                "model": models[0],
                "base_url": "http://127.0.0.1:11434",
                "importance_threshold": 0.65,
            }

    print("Ollama was not selected. Configure any provider using an OpenAI-compatible endpoint.")
    provider = input("LLM provider [openai-compatible]: ").strip() or "openai-compatible"
    model = _prompt_non_empty("LLM model (for example gpt-4.1-mini): ")
    default_base = "https://api.openai.com"
    base_url = input(f"Base URL [{default_base}]: ").strip() or default_base
    threshold_input = input("Importance threshold 0-1 [0.65]: ").strip()
    try:
        threshold = float(threshold_input) if threshold_input else 0.65
    except ValueError:
        threshold = 0.65

    api_key = input("API key (optional, press Enter to skip): ").strip()
    if api_key:
        cache_llm_api_key(api_key)

    return {
        "provider": provider,
        "model": model,
        "base_url": base_url,
        "importance_threshold": max(0.0, min(1.0, threshold)),
    }


def run_onboarding_wizard() -> None:
    print("\n== forgetMail onboarding ==")

    print("\n[1/3] Google OAuth")
    secret_path = _import_client_secret()
    get_credentials(client_secret_path=secret_path, allow_reauth=True)
    print(f"Google credentials saved. Client secret stored at {secret_path}.")

    print("\n[2/3] Telegram")
    print("Create a bot using @BotFather, copy token, and send any message to your bot.")
    token = _prompt_non_empty("Bot token: ")
    bot_info = validate_token(token)
    cache_bot_token(token)
    ensure_polling_mode(token, drop_pending_updates=False)
    chat_id = _detect_chat_id_with_retry(token)
    print(f"Telegram bot validated: @{bot_info['username']}")
    print(f"Detected chat_id: {chat_id}")

    llm_config = _onboard_llm()

    config = {
        "telegram": {
            "chat_id": chat_id,
            "mode": "polling",
        },
        "gmail": {
            "poll_interval_seconds": 180,
            "lookback_days": 7,
            "max_messages_per_poll": 30,
        },
        "llm": llm_config,
        "log": {
            "level": "INFO",
        },
    }
    save_config(config)
    print(f"Config written to {CONFIG_PATH}")

    print("\nRunning connectivity checks...")
    try:
        validate_all()
        print("\nOnboarding complete.")
    except Exception as exc:
        print(f"Connectivity checks did not fully complete: {exc}")
        print("Onboarding data was saved. You can re-run checks with forgetMail --check.")


def run_auth_wizard() -> None:
    run_onboarding_wizard()


def validate_all() -> None:
    config = load_config()
    refresh_timeout_seconds = int(os.getenv("FORGETMAIL_GOOGLE_REFRESH_TIMEOUT_SECONDS", "30"))

    print("Checking Gmail API...", flush=True)
    profile = None
    last_error: Exception | None = None
    for attempt in range(1, 3):
        try:
            print(f"  Gmail attempt {attempt}/2", flush=True)
            creds = get_credentials(allow_reauth=False, refresh_timeout_seconds=refresh_timeout_seconds)
            gmail = GmailClient(creds, timeout_seconds=15)
            profile = gmail.get_profile()
            break
        except Exception as exc:
            last_error = exc
            if _is_connectivity_failure(exc):
                break
            if attempt < 2:
                time.sleep(attempt * 2)

    if profile is None:
        raise RuntimeError(f"Gmail API check failed after retries: {last_error}")

    print(f"Gmail API reachable for: {profile.get('emailAddress', 'unknown')}.")

    print("Checking Telegram API...", flush=True)
    token = get_bot_token()
    bot = validate_token(token)
    print(f"Telegram API reachable for bot: @{bot.get('username', 'unknown')}.")
    print(f"Configured chat_id: {config['telegram']['chat_id']}")

    print("Checking LLM provider...", flush=True)
    llm_status = validate_llm_connection(config["llm"])
    print(f"LLM check passed: {llm_status}")
