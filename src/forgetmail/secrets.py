from __future__ import annotations

import os

import keyring

SERVICE_NAME = "forgetmail"


def _env_var_name(key: str) -> str:
    return f"FORGETMAIL_{key.upper()}"


def get_secret(key: str) -> str | None:
    env_value = os.getenv(_env_var_name(key))
    if env_value:
        return env_value

    try:
        return keyring.get_password(SERVICE_NAME, key)
    except Exception:
        return None


def set_secret(key: str, value: str) -> bool:
    try:
        keyring.set_password(SERVICE_NAME, key, value)
        return True
    except Exception:
        return False
