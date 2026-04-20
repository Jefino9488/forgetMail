from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key.startswith("_"):
                continue
            if key in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }:
                continue
            if key not in payload:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True, default=str)


def _setup_logging(
    level_name: str,
    debug: bool = False,
    log_file: str | None = None,
    http_debug: bool = False,
) -> None:
    level = logging.DEBUG if debug else getattr(logging, level_name.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if isinstance(log_file, str) and log_file.strip():
        file_path = Path(log_file).expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(file_path, encoding="utf-8"))
    formatter = _JsonFormatter()
    for handler in handlers:
        handler.setFormatter(formatter)
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,
    )
    if not http_debug:
        for logger_name in (
            "httpcore",
            "httpx",
            "urllib3",
            "keyring",
            "google.auth.transport.requests",
        ):
            logging.getLogger(logger_name).setLevel(logging.WARNING)
