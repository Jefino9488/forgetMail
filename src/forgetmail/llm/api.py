from __future__ import annotations

import json
from typing import Any

from .parsing import _validate_answer_payload
from .providers import _call_ollama_json, _call_openai_compatible_json


def call_classifier_json(
    llm_config: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    provider = str(llm_config.get("provider", "")).strip().lower()
    if provider == "ollama":
        return _call_ollama_json(
            llm_config, system_prompt, user_prompt, timeout_seconds
        )
    return _call_openai_compatible_json(
        llm_config, system_prompt, user_prompt, timeout_seconds
    )


def call_answer_json(
    llm_config: dict[str, Any],
    *,
    question: str,
    context_rows: list[dict[str, Any]],
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    max_citations = max(1, int(llm_config.get("ask_max_citations", 3)))
    system_prompt = (
        "You answer inbox question. Use only given email context. "
        "If not sure, say unsure. "
        "Return JSON only with this schema: "
        '{"answer":"string","confidence":0.0,"citations":[{"message_id":"string","subject":"string","why":"string"}]}'
    )
    user_prompt = json.dumps(
        {
            "question": question,
            "max_citations": max_citations,
            "context": context_rows,
        },
        ensure_ascii=True,
    )
    payload = call_classifier_json(
        llm_config,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        timeout_seconds=timeout_seconds,
    )
    return _validate_answer_payload(payload, max_citations=max_citations)
