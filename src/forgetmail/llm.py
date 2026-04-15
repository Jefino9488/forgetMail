from __future__ import annotations

import json
from typing import Any

import httpx

from forgetmail.secrets import get_secret, set_secret

LLM_API_KEY_SECRET = "llm_api_key"


class LLMError(RuntimeError):
    pass


def cache_llm_api_key(api_key: str) -> None:
    if not set_secret(LLM_API_KEY_SECRET, api_key):
        raise RuntimeError(
            "Could not store LLM API key in keyring. "
            "Set FORGETMAIL_LLM_API_KEY as an environment variable."
        )


def get_llm_api_key() -> str | None:
    return get_secret(LLM_API_KEY_SECRET)


def detect_ollama_models(base_url: str = "http://127.0.0.1:11434") -> list[str]:
    try:
        response = httpx.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        response.raise_for_status()
    except Exception:
        return []

    data = response.json()
    models: list[str] = []
    for item in data.get("models", []):
        name = item.get("name")
        if isinstance(name, str) and name:
            models.append(name)
    return models


def validate_llm_connection(llm_config: dict[str, Any]) -> str:
    provider = str(llm_config.get("provider", "")).strip().lower()
    model = str(llm_config.get("model", "")).strip()
    base_url = str(llm_config.get("base_url", "")).strip()

    if provider == "ollama":
        models = detect_ollama_models(base_url or "http://127.0.0.1:11434")
        if not models:
            raise RuntimeError("Ollama server not reachable or no models installed.")
        if model not in models:
            raise RuntimeError(f"Configured Ollama model '{model}' was not found.")
        return f"Ollama model '{model}' is available"

    if not base_url:
        raise RuntimeError("llm.base_url is required for non-Ollama providers.")

    headers = {}
    api_key = get_llm_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = httpx.get(f"{base_url.rstrip('/')}/v1/models", headers=headers, timeout=10)
    response.raise_for_status()
    return f"Provider '{provider}' reachable via {base_url}"


def call_classifier_json(
    llm_config: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    provider = str(llm_config.get("provider", "")).strip().lower()
    if provider == "ollama":
        return _call_ollama_json(llm_config, system_prompt, user_prompt, timeout_seconds)
    return _call_openai_compatible_json(llm_config, system_prompt, user_prompt, timeout_seconds)


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


def _call_ollama_json(
    llm_config: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    model = str(llm_config.get("model", "")).strip()
    if not model:
        raise LLMError("llm.model is required for Ollama provider.")

    base_url = str(llm_config.get("base_url", "http://127.0.0.1:11434")).strip() or "http://127.0.0.1:11434"
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": _resolve_temperature(llm_config)},
    }

    response = httpx.post(f"{base_url.rstrip('/')}/api/chat", json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    data = response.json()
    content = data.get("message", {}).get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise LLMError("Ollama returned an empty response.")
    return _extract_json_payload(content)


def _call_openai_compatible_json(
    llm_config: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    model = str(llm_config.get("model", "")).strip()
    base_url = str(llm_config.get("base_url", "")).strip()
    if not model:
        raise LLMError("llm.model is required for non-Ollama providers.")
    if not base_url:
        raise LLMError("llm.base_url is required for non-Ollama providers.")

    headers = {"Content-Type": "application/json"}
    api_key = get_llm_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": _resolve_temperature(llm_config),
        "response_format": {"type": "json_object"},
    }

    response = httpx.post(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise LLMError("Provider returned no choices.")
    content = choices[0].get("message", {}).get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise LLMError("Provider returned empty content.")
    return _extract_json_payload(content)
