from __future__ import annotations

from typing import Any

from .models import EmailCandidate, EmailClassification


def _parse_important_flag(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    return None


def _parse_rows(
    rows: list[object],
    by_id: dict[str, EmailCandidate],
    *,
    schema_strict: bool,
) -> list[EmailClassification]:
    parsed: list[EmailClassification] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        message_id = str(row.get("message_id", "")).strip()
        if not message_id or message_id not in by_id:
            continue

        important_value = _parse_important_flag(row.get("important"))
        if important_value is None:
            if schema_strict:
                continue
            important_value = False

        score_raw = row.get("score", 0.0)
        try:
            score = float(score_raw)
        except (TypeError, ValueError):
            if schema_strict:
                continue
            score = 0.0
        if schema_strict and (score < 0.0 or score > 1.0):
            continue
        score = max(0.0, min(1.0, score))

        reason = str(row.get("reason", "")).strip() or "No reason provided"
        if schema_strict and reason == "No reason provided":
            continue

        parsed.append(
            EmailClassification(
                message_id=message_id,
                important=important_value,
                score=score,
                reason=reason,
            )
        )
    return parsed
