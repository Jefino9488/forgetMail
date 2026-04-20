from __future__ import annotations

try:
    import keyring
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    keyring = None

SERVICE_NAME = "forgetmail"


def get_keyring_secret(key: str) -> str | None:
    if keyring is None:
        return None
    try:
        return keyring.get_password(SERVICE_NAME, key)
    except Exception:
        return None


def set_keyring_secret(key: str, value: str) -> bool:
    if keyring is None:
        return False
    try:
        keyring.set_password(SERVICE_NAME, key, value)
        return True
    except Exception:
        return False
