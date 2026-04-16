from pathlib import Path

from forgetmail.config import CONFIG_DIR

STATE_DB_PATH = CONFIG_DIR / "state.db"

__all__ = ["STATE_DB_PATH", "Path"]
