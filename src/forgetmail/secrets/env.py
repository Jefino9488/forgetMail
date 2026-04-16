from __future__ import annotations

import os


def _env_var_name(key: str) -> str:
    return f"FORGETMAIL_{key.upper()}"


def get_env_secret(key: str) -> str | None:
    env_value = os.getenv(_env_var_name(key))
    if env_value:
        return env_value
    return None
