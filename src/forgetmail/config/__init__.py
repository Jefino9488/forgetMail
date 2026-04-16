from __future__ import annotations

from copy import deepcopy
from typing import Any

import tomllib

from .defaults import CONFIG_DIR, CONFIG_PATH, DEFAULT_CONFIG
from .validation import ConfigError, validate_config


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


__all__ = [
    "CONFIG_DIR",
    "CONFIG_PATH",
    "DEFAULT_CONFIG",
    "ConfigError",
    "ensure_config_dir",
    "save_config",
    "load_config",
    "merge_config",
    "validate_config",
]
