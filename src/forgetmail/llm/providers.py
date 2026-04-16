from __future__ import annotations

from typing import Any

import httpx

from .auth import get_llm_api_key
from .errors import LLMError
from .parsing import _extract_json_payload, _resolve_temperature


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


def _call_ollama_json(
    llm_config: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    model = str(llm_config.get("model", "")).strip()
    if not model:
        raise LLMError("llm.model is required for Ollama provider.")

    base_url = (
        str(llm_config.get("base_url", "http://127.0.0.1:11434")).strip()
        or "http://127.0.0.1:11434"
    )
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
