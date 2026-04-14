from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import tomllib

CONFIG_DIR = Path.home() / ".config" / "forgetmail"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG: dict[str, Any] = {
    "telegram": {
        "chat_id": 0,
        "mode": "polling",
    },
    "gmail": {
        "poll_interval_seconds": 180,
        "idle_poll_interval_seconds": 180,
        "lookback_days": 7,
        "max_messages_per_poll": 30,
    },
    "llm": {
        "provider": "ollama",
        "model": "",
        "base_url": "http://127.0.0.1:11434",
        "importance_threshold": 0.65,
        "timeout_seconds": 180,
        "batch_size": 8,
    },
    "log": {
        "level": "INFO",
        "file": "",
        "http_debug": False,
    },
}


class ConfigError(RuntimeError):
    pass


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_config(config: dict[str, Any]) -> None:
    import tomli_w

    ensure_config_dir()
    with CONFIG_PATH.open("wb") as file_obj:
        tomli_w.dump(config, file_obj)


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise ConfigError("Config not found. Run forgetMail --onboard first.")

    with CONFIG_PATH.open("rb") as file_obj:
        loaded = tomllib.load(file_obj)

    merged = merge_config(loaded)
    validate_config(merged)
    return merged


def merge_config(config: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(DEFAULT_CONFIG)
    for section, section_values in config.items():
        if isinstance(section_values, dict) and isinstance(result.get(section), dict):
            result[section].update(section_values)
        else:
            result[section] = section_values
    return result


def validate_config(config: dict[str, Any]) -> None:
    required_sections = ("telegram", "gmail", "llm", "log")
    for section in required_sections:
        if section not in config or not isinstance(config[section], dict):
            raise ConfigError(f"Missing or invalid [{section}] section in config.")

    chat_id = config["telegram"].get("chat_id")
    if not isinstance(chat_id, int) or chat_id == 0:
        raise ConfigError("telegram.chat_id must be a non-zero integer.")

    interval = config["gmail"].get("poll_interval_seconds")
    if not isinstance(interval, int) or interval < 30:
        raise ConfigError("gmail.poll_interval_seconds must be an integer >= 30.")

    idle_interval = config["gmail"].get("idle_poll_interval_seconds", interval)
    if not isinstance(idle_interval, int) or idle_interval < 30:
        raise ConfigError("gmail.idle_poll_interval_seconds must be an integer >= 30.")

    lookback_days = config["gmail"].get("lookback_days")
    if not isinstance(lookback_days, int) or lookback_days < 1:
        raise ConfigError("gmail.lookback_days must be an integer >= 1.")

    max_messages = config["gmail"].get("max_messages_per_poll")
    if not isinstance(max_messages, int) or max_messages < 1:
        raise ConfigError("gmail.max_messages_per_poll must be an integer >= 1.")

    provider = config["llm"].get("provider")
    if not isinstance(provider, str) or not provider.strip():
        raise ConfigError("llm.provider must be a non-empty string.")

    provider_name = provider.strip().lower()

    model = config["llm"].get("model")
    if not isinstance(model, str) or not model.strip():
        raise ConfigError("llm.model must be a non-empty string.")

    base_url = config["llm"].get("base_url")
    if not isinstance(base_url, str):
        raise ConfigError("llm.base_url must be a string.")
    if provider_name != "ollama" and not base_url.strip():
        raise ConfigError("llm.base_url must be set for non-Ollama providers.")
    if provider_name == "ollama" and not base_url.strip():
        raise ConfigError("llm.base_url must be set for Ollama provider.")

    threshold = config["llm"].get("importance_threshold")
    if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
        raise ConfigError("llm.importance_threshold must be a number between 0 and 1.")

    timeout_seconds = config["llm"].get("timeout_seconds")
    if not isinstance(timeout_seconds, int) or timeout_seconds < 5:
        raise ConfigError("llm.timeout_seconds must be an integer >= 5.")

    batch_size = config["llm"].get("batch_size")
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ConfigError("llm.batch_size must be an integer >= 1.")

    log_level = config["log"].get("level")
    if not isinstance(log_level, str) or not log_level.strip():
        raise ConfigError("log.level must be a non-empty string.")

    log_file = config["log"].get("file", "")
    if not isinstance(log_file, str):
        raise ConfigError("log.file must be a string.")

    http_debug = config["log"].get("http_debug", False)
    if not isinstance(http_debug, bool):
        raise ConfigError("log.http_debug must be true or false.")
