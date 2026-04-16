from __future__ import annotations


def classification_event_row_to_dict(
    raw: tuple[object, ...],
) -> dict[str, str | float | int]:
    return {
        "message_id": str(raw[0]),
        "thread_id": str(raw[1]),
        "sender": str(raw[2]),
        "subject": str(raw[3]),
        "important": int(raw[4]),
        "score": float(raw[5]),
        "reason": str(raw[6]),
        "provider": str(raw[7]),
        "model": str(raw[8]),
        "classified_at": str(raw[9]),
    }


def watch_rule_row_to_dict(raw: tuple[object, ...]) -> dict[str, str | float | int]:
    return {
        "id": int(raw[0]),
        "context": str(raw[1]),
        "boost": float(raw[2]),
        "is_active": int(raw[3]),
        "created_at": str(raw[4]),
    }


def signal_event_row_to_dict(raw: tuple[object, ...]) -> dict[str, str | float]:
    return {
        "message_id": str(raw[0]),
        "thread_id": str(raw[1]),
        "sender": str(raw[2]),
        "subject": str(raw[3]),
        "reason": str(raw[4]),
        "score": float(raw[5]),
        "notified_at": str(raw[6]),
    }


def feedback_correction_row_to_dict(
    raw: tuple[object, ...],
) -> dict[str, str | float | int]:
    return {
        "id": int(raw[0]),
        "message_id": str(raw[1]),
        "thread_id": str(raw[2]),
        "original_important": int(raw[3]),
        "original_score": float(raw[4]),
        "original_reason": str(raw[5]),
        "corrected_important": int(raw[6]),
        "correction_source": str(raw[7]),
        "created_at": str(raw[8]),
    }
