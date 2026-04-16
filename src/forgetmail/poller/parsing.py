from __future__ import annotations


def _header_map(headers: list[dict[str, str]]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for item in headers:
        key = item.get("name")
        value = item.get("value")
        if isinstance(key, str) and isinstance(value, str):
            mapped[key.lower()] = value
    return mapped
