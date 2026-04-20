from __future__ import annotations

from datetime import datetime
from email.utils import parseaddr
from typing import Any


def _normalize_email_address(raw_value: str) -> tuple[str, str]:
    display_name, email_address = parseaddr(raw_value)
    normalized_email = email_address.strip().lower()
    if not normalized_email and raw_value.strip():
        normalized_email = raw_value.strip().lower()
    return normalized_email, display_name.strip()


def _cache_key_for(name: str) -> str:
    return f"daemon:{name}"


def _heartbeat_due_now(
    now: datetime, heartbeat_local_time: str, last_sent_date: str | None
) -> bool:
    time_text = heartbeat_local_time.strip()
    try:
        hour_text, minute_text = time_text.split(":", maxsplit=1)
        target_hour = int(hour_text)
        target_minute = int(minute_text)
    except Exception:
        target_hour = 9
        target_minute = 0

    local_now = now.astimezone()
    if last_sent_date == local_now.date().isoformat():
        return False
    if local_now.hour < target_hour:
        return False
    if local_now.hour == target_hour and local_now.minute < target_minute:
        return False
    return True


def _credential_refresh_warning_key(detail: str) -> str:
    return f"{_cache_key_for('credential_refresh_warning')}:{detail.strip().lower()}"


def _is_connectivity_failure(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "name or service not known",
        "gaierror",
        "dns",
        "temporary failure in name resolution",
        "connection timed out",
        "read timed out",
        "max retries exceeded",
        "connection aborted",
        "connection reset",
        "network is unreachable",
    )
    return any(marker in text for marker in markers)


def _looks_like_newsletter(sender: str, subject: str, snippet: str) -> bool:
    merged = f"{sender} {subject} {snippet}".lower()
    newsletter_markers = [
        "newsletter",
        "digest",
        "unsubscribe",
        "sponsored",
        "promotion",
        "theresanaiforthat",
    ]
    personal_markers = [
        "can you",
        "please",
        "asap",
        "urgent",
        "meeting",
        "schedule",
        "reply",
        "action required",
    ]
    has_newsletter_signal = any(item in merged for item in newsletter_markers)
    has_personal_signal = any(item in merged for item in personal_markers)
    return has_newsletter_signal and not has_personal_signal


def _distance_to_similarity(distance_value: Any) -> float | None:
    try:
        distance = float(distance_value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, 1.0 - distance))


def _select_poll_interval_seconds(
    *,
    active_interval_seconds: int,
    idle_interval_seconds: int,
    last_cycle: dict[str, int] | None,
) -> int:
    if not last_cycle:
        return active_interval_seconds
    if int(last_cycle.get("llm_failed", 0)) > 0:
        return active_interval_seconds
    if int(last_cycle.get("unseen", 0)) == 0:
        return idle_interval_seconds
    return active_interval_seconds
