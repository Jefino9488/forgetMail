from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from forgetmail.llm import LLMError, call_classifier_json


@dataclass
class EmailCandidate:
    message_id: str
    thread_id: str
    sender: str
    subject: str
    snippet: str


@dataclass
class EmailClassification:
    message_id: str
    important: bool
    score: float
    reason: str


def _heuristic_classifications(messages: list[EmailCandidate], failure_reason: str) -> list[EmailClassification]:
    logging.debug("Classifier: using heuristic fallback due to '%s'", failure_reason)
    keywords = ("urgent", "asap", "meeting", "schedule", "today", "tomorrow", "deadline", "please respond")
    rows: list[EmailClassification] = []
    for item in messages:
        haystack = f"{item.subject} {item.snippet}".lower()
        matched = any(keyword in haystack for keyword in keywords)
        rows.append(
            EmailClassification(
                message_id=item.message_id,
                important=matched,
                score=0.7 if matched else 0.2,
                reason=(
                    "Heuristic fallback used due to classifier timeout"
                    if matched
                    else f"Heuristic fallback: no urgency keywords ({failure_reason})"
                ),
            )
        )
    return rows


def classify_messages(messages: list[EmailCandidate], llm_config: dict) -> list[EmailClassification]:
    if not messages:
        return []

    logging.debug(
        "Classifier: starting batch size=%s provider=%s model=%s",
        len(messages),
        llm_config.get("provider"),
        llm_config.get("model"),
    )

    compact = [
        {
            "message_id": item.message_id,
            "from": item.sender,
            "subject": item.subject,
            "snippet": item.snippet[:500],
        }
        for item in messages
    ]

    system_prompt = (
        "You classify unread emails as important signal or noise. "
        "Signal means direct human request, urgent task, meeting coordination, or time-sensitive action. "
        "Noise means newsletters, marketing, automated updates, receipts, and low-priority notifications. "
        "Return strict JSON object with key 'results', where each item includes message_id, important, score, reason. "
        "score must be 0..1, important must be boolean."
    )
    user_prompt = json.dumps({"emails": compact}, ensure_ascii=True)

    timeout_seconds = int(llm_config.get("timeout_seconds", 90))
    try:
        payload = call_classifier_json(llm_config, system_prompt, user_prompt, timeout_seconds=timeout_seconds)
    except Exception as exc:
        logging.debug("Classifier: LLM call failed, switching to fallback")
        return _heuristic_classifications(messages, str(exc))

    rows = payload.get("results", [])
    if not isinstance(rows, list):
        raise LLMError("LLM response missing 'results' list.")
    logging.debug("Classifier: LLM returned rows=%s", len(rows))

    by_id = {item.message_id: item for item in messages}
    parsed: list[EmailClassification] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        message_id = str(row.get("message_id", "")).strip()
        if not message_id or message_id not in by_id:
            continue
        important = bool(row.get("important", False))
        score_raw = row.get("score", 0.0)
        try:
            score = float(score_raw)
        except (TypeError, ValueError):
            score = 0.0
        score = max(0.0, min(1.0, score))
        reason = str(row.get("reason", "")).strip() or "No reason provided"
        parsed.append(
            EmailClassification(
                message_id=message_id,
                important=important,
                score=score,
                reason=reason,
            )
        )

    existing_ids = {item.message_id for item in parsed}
    for item in messages:
        if item.message_id not in existing_ids:
            parsed.append(
                EmailClassification(
                    message_id=item.message_id,
                    important=False,
                    score=0.0,
                    reason="Classifier omitted this message",
                )
            )

            logging.debug("Classifier: final parsed rows=%s", len(parsed))
    return parsed
