from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

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


def _chunk_messages(messages: list[EmailCandidate], chunk_size: int) -> list[list[EmailCandidate]]:
    size = max(1, chunk_size)
    return [messages[index : index + size] for index in range(0, len(messages), size)]


def _parse_important_flag(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    return None


def _format_few_shot_examples(few_shot_examples: list[dict[str, Any]] | None) -> str:
    if not few_shot_examples:
        return ""

    lines = ["Examples:"]
    for item in few_shot_examples:
        important = bool(item.get("important", False))
        label = 1 if important else 0
        text = str(item.get("text", "")).strip()
        reason = str(item.get("reason", "user correction")).strip() or "user correction"
        if not text:
            continue
        text_value = " ".join(text.split())
        if len(text_value) > 180:
            text_value = text_value[:177].rstrip() + "..."
        lines.append(f"- {text_value} => important={label} reason={reason}")

    if len(lines) == 1:
        return ""
    return "\n" + "\n".join(lines)


def _build_system_prompt(llm_config: dict[str, Any], few_shot_examples: list[dict[str, Any]] | None) -> str:
    style = str(llm_config.get("prompt_style", "caveman")).strip().lower()
    schema = (
        '{"results":[{"message_id":"string","important":true,"score":0.0,"reason":"string"}]}'
    )
    if style == "verbose":
        base = (
            "You classify unread emails as important signal or noise. "
            "Signal means direct human request, urgent task, meeting coordination, or time-sensitive action. "
            "Noise means newsletters, marketing, automated updates, receipts, and low-priority notifications. "
            "Return strict JSON only. Schema: "
            f"{schema}. "
            "Return one result per input email and keep message_id unchanged."
        )
        return base + _format_few_shot_examples(few_shot_examples)

    base = (
        "Classify inbox mail. important=1 if human ask/urgent/action. else 0 for promo/news/automated. "
        "Return JSON only. Schema: "
        f"{schema}. "
        "Keep all input message_id exactly once. score in [0,1]."
    )
    return base + _format_few_shot_examples(few_shot_examples)


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


def _classify_chunk(
    messages: list[EmailCandidate],
    llm_config: dict,
    timeout_seconds: int,
    few_shot_examples: list[dict[str, Any]] | None,
) -> list[EmailClassification]:
    if not messages:
        return []

    compact = [
        {
            "message_id": item.message_id,
            "from": item.sender,
            "subject": item.subject,
            "snippet": item.snippet[:500],
        }
        for item in messages
    ]

    ids_csv = ",".join(item.message_id for item in messages)
    schema_strict = bool(llm_config.get("schema_strict", True))
    system_prompt = _build_system_prompt(llm_config, few_shot_examples)
    user_prompt = json.dumps(
        {
            "required_message_ids": [item.message_id for item in messages],
            "required_count": len(messages),
            "required_ids_csv": ids_csv,
            "emails": compact,
        },
        ensure_ascii=True,
    )

    payload = call_classifier_json(llm_config, system_prompt, user_prompt, timeout_seconds=timeout_seconds)
    rows = payload.get("results", [])
    if not isinstance(rows, list):
        raise LLMError("LLM response missing 'results' list.")

    by_id = {item.message_id: item for item in messages}
    parsed = _parse_rows(rows, by_id, schema_strict=schema_strict)
    if parsed and len(parsed) == len(messages):
        return parsed

    missing_ids = [item.message_id for item in messages if item.message_id not in {row.message_id for row in parsed}]
    if not missing_ids:
        return parsed

    logging.debug("Classifier: retrying missing ids chunk_size=%s missing=%s", len(messages), len(missing_ids))
    retry_messages = [item for item in messages if item.message_id in set(missing_ids)]
    retry_compact = [
        {
            "message_id": item.message_id,
            "from": item.sender,
            "subject": item.subject,
            "snippet": item.snippet[:500],
        }
        for item in retry_messages
    ]
    retry_prompt = json.dumps(
        {
            "required_message_ids": [item.message_id for item in retry_messages],
            "required_count": len(retry_messages),
            "emails": retry_compact,
        },
        ensure_ascii=True,
    )
    retry_payload = call_classifier_json(llm_config, system_prompt, retry_prompt, timeout_seconds=timeout_seconds)
    retry_rows = retry_payload.get("results", [])
    if isinstance(retry_rows, list):
        parsed.extend(_parse_rows(retry_rows, by_id, schema_strict=schema_strict))

    deduped: dict[str, EmailClassification] = {}
    for item in parsed:
        deduped[item.message_id] = item
    return list(deduped.values())

def classify_messages(
    messages: list[EmailCandidate],
    llm_config: dict,
    *,
    few_shot_examples: list[dict[str, Any]] | None = None,
) -> list[EmailClassification]:
    if not messages:
        return []

    logging.debug(
        "Classifier: starting batch size=%s provider=%s model=%s",
        len(messages),
        llm_config.get("provider"),
        llm_config.get("model"),
    )

    timeout_seconds = int(llm_config.get("timeout_seconds", 180))
    chunk_size = int(llm_config.get("batch_size", 8))
    try:
        parsed: list[EmailClassification] = []
        chunks = _chunk_messages(messages, chunk_size)
        logging.debug("Classifier: chunking enabled chunks=%s chunk_size=%s", len(chunks), chunk_size)
        for chunk in chunks:
            parsed.extend(
                _classify_chunk(
                    chunk,
                    llm_config,
                    timeout_seconds=timeout_seconds,
                    few_shot_examples=few_shot_examples,
                )
            )
    except Exception as exc:
        logging.warning("Classifier: LLM call failed; strict mode skips this batch")
        raise LLMError(f"Classifier call failed: {exc}") from exc
    logging.debug("Classifier: parsed rows=%s", len(parsed))

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
