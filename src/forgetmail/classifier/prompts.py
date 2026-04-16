from __future__ import annotations

from typing import Any


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


def _build_system_prompt(
    llm_config: dict[str, Any], few_shot_examples: list[dict[str, Any]] | None
) -> str:
    style = str(llm_config.get("prompt_style", "caveman")).strip().lower()
    schema = '{"results":[{"message_id":"string","important":true,"score":0.0,"reason":"string"}]}'
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
