from __future__ import annotations

from pathlib import Path
from typing import Any

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
        "prompt_style": "caveman",
        "temperature": 0.1,
        "schema_strict": True,
        "ask_enabled": True,
        "ask_top_k": 6,
        "ask_timeout_seconds": 90,
        "ask_max_context_chars": 3500,
        "ask_max_citations": 3,
        "ask_min_confidence": 0.5,
        "few_shot_max_examples": 4,
    },
    "embeddings": {
        "enabled": False,
        "enable_vector_upsert": True,
        "enable_vector_query": False,
        "query_top_k": 6,
        "min_similarity_for_boost": 0.78,
        "max_similarity_boost": 0.20,
        "min_important_neighbors": 1,
        "provider": "ollama",
        "model": "nomic-embed-text",
        "base_url": "http://127.0.0.1:11434",
        "batch_size": 32,
        "timeout_seconds": 30,
        "persist_path": str(CONFIG_DIR / "chroma"),
        "collection": "emails",
        "enable_corrections": True,
        "corrections_collection": "email_corrections",
        "corrections_top_k": 2,
        "corrections_min_similarity": 0.72,
    },
    "log": {
        "level": "INFO",
        "file": "",
        "http_debug": False,
    },
    "service": {
        "install_type": "user",
        "linger": True,
    },
    "health": {
        "heartbeat_enabled": True,
        "heartbeat_local_time": "09:00",
        "watchdog_failure_threshold": 3,
        "watchdog_retry_base_seconds": 2,
        "watchdog_retry_max_seconds": 30,
    },
}
