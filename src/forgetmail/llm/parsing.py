from __future__ import annotations

import json
from typing import Any

from .errors import LLMError


def _extract_json_payload(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMError(f"LLM returned invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise LLMError("LLM response JSON must be an object.")
    return payload


def _resolve_temperature(llm_config: dict[str, Any]) -> float:
    value = llm_config.get("temperature", 0.1)
    try:
        temperature = float(value)
    except (TypeError, ValueError):
        return 0.1
    return max(0.0, min(1.0, temperature))


def _validate_answer_payload(payload: dict[str, Any], *, max_citations: int) -> dict[str, Any]:
    answer = payload.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise LLMError("LLM answer payload missing non-empty 'answer'.")

    confidence_raw = payload.get("confidence", 0.0)
    try:
        confidence = float(confidence_raw)
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    citations_raw = payload.get("citations", [])
    if not isinstance(citations_raw, list):
        raise LLMError("LLM answer payload field 'citations' must be a list.")

    citations: list[dict[str, str]] = []
    for item in citations_raw[:max_citations]:
        if not isinstance(item, dict):
            continue
        message_id = item.get("message_id")
        subject = item.get("subject")
        why = item.get("why")
        if not isinstance(message_id, str) or not message_id.strip():
            continue
        subject_value = str(subject or "(no subject)").strip() or "(no subject)"
        why_value = str(why or "relevant context").strip() or "relevant context"
        citations.append(
            {
                "message_id": message_id.strip(),
                "subject": subject_value,
                "why": why_value,
            }
        )

    return {
        "answer": answer.strip(),
        "confidence": confidence,
        "citations": citations,
    }
