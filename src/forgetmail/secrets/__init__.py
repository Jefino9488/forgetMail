from .env import get_env_secret
from .keyring_store import SERVICE_NAME, get_keyring_secret, set_keyring_secret


def get_secret(key: str) -> str | None:
    env_value = get_env_secret(key)
    if env_value:
        return env_value
    return get_keyring_secret(key)


def set_secret(key: str, value: str) -> bool:
    return set_keyring_secret(key, value)


__all__ = ["SERVICE_NAME", "get_secret", "set_secret"]
