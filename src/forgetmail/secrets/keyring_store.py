from __future__ import annotations

import keyring

SERVICE_NAME = "forgetmail"


def get_keyring_secret(key: str) -> str | None:
    try:
        return keyring.get_password(SERVICE_NAME, key)
    except Exception:
        return None


def set_keyring_secret(key: str, value: str) -> bool:
    try:
        keyring.set_password(SERVICE_NAME, key, value)
        return True
    except Exception:
        return False
