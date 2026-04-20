from __future__ import annotations

from typing import Any

from forgetmail.config import save_config
from forgetmail.store import StateStore

from .common import _normalize_email_address


def _help_text() -> str:
    return (
        "forgetMail bot commands:\n"
        "/help - show this help\n"
        "/status - runtime and DB stats\n"
        "/signals - show recent signal notifications\n"
        "/ask <question> - chat with your inbox\n"
        "/watchFor <context> [boost] - prioritize matching emails\n"
        "/watchList - list active watch rules\n"
        "/unwatch <rule_id> - delete a watch rule\n"
        "/set archive on|off - enable or disable auto-archive\n"
        "/vip add|list|remove - manage VIP senders\n"
        "/run - trigger an immediate poll cycle"
    )


def _format_recent_signals(rows: list[dict[str, str | float]]) -> str:
    if not rows:
        return "No signal notifications recorded yet."

    lines = ["Recent signals:"]
    for item in rows:
        lines.append(
            (f"- {item['notified_at']} | {item['subject']} | score={float(item['score']):.2f}")
        )
    return "\n".join(lines)


def _format_status(
    config: dict[str, Any], store: StateStore, last_cycle: dict[str, int] | None
) -> str:
    stats = store.stats()
    llm_cfg = config["llm"]
    embeddings_cfg = config.get("embeddings", {})
    gmail_cfg = config["gmail"]
    health_cfg = config.get("health", {})
    service_cfg = config.get("service", {})
    lines = [
        "forgetMail status:",
        f"- poll_interval_seconds: {gmail_cfg['poll_interval_seconds']}",
        f"- idle_poll_interval_seconds: {gmail_cfg.get('idle_poll_interval_seconds', gmail_cfg['poll_interval_seconds'])}",
        f"- lookback_days: {gmail_cfg['lookback_days']}",
        f"- max_messages_per_poll: {gmail_cfg['max_messages_per_poll']}",
        f"- auto_label_enabled: {bool(gmail_cfg.get('auto_label_enabled', True))}",
        f"- archive_noise: {bool(gmail_cfg.get('archive_noise', False))}",
        f"- signal_label: {gmail_cfg.get('signal_label', 'forgetMail/signal')}",
        f"- noise_label: {gmail_cfg.get('noise_label', 'forgetMail/noise')}",
        f"- llm_provider: {llm_cfg['provider']}",
        f"- llm_model: {llm_cfg['model']}",
        f"- llm_prompt_style: {llm_cfg.get('prompt_style', 'caveman')}",
        f"- importance_threshold: {llm_cfg['importance_threshold']}",
        f"- heartbeat_enabled: {bool(health_cfg.get('heartbeat_enabled', True))}",
        f"- heartbeat_local_time: {health_cfg.get('heartbeat_local_time', '09:00')}",
        f"- watchdog_failure_threshold: {health_cfg.get('watchdog_failure_threshold', 3)}",
        f"- service_install_type: {service_cfg.get('install_type', 'user')}",
        f"- service_linger: {bool(service_cfg.get('linger', True))}",
        f"- embeddings_enabled: {bool(embeddings_cfg.get('enabled', False))}",
        f"- embeddings_model: {embeddings_cfg.get('model', 'n/a')}",
        f"- vector_upsert_enabled: {bool(embeddings_cfg.get('enable_vector_upsert', False))}",
        f"- vector_query_enabled: {bool(embeddings_cfg.get('enable_vector_query', False))}",
        f"- vector_query_top_k: {embeddings_cfg.get('query_top_k', 'n/a')}",
        f"- seen_messages: {stats['seen_messages']}",
        f"- signal_events: {stats['signal_events']}",
        f"- classification_events: {stats['classification_events']}",
        f"- watch_rules: {stats['watch_rules']}",
        f"- watch_rule_events: {stats['watch_rule_events']}",
        f"- muted_threads: {stats['muted_threads']}",
        f"- muted_messages: {stats.get('muted_messages', 0)}",
        f"- vip_senders: {stats.get('vip_senders', 0)}",
        f"- feedback_corrections: {stats.get('feedback_corrections', 0)}",
    ]

    if last_cycle:
        lines.append(
            (
                "- last_cycle: "
                f"fetched={last_cycle['fetched']} unseen={last_cycle['unseen']} "
                f"classified={last_cycle['classified']} "
                f"boosted={last_cycle['boosted']} "
                f"signals={last_cycle['signals']} sent={last_cycle['sent']} "
                f"gmail_marked_read={last_cycle.get('gmail_marked_read', 0)} "
                f"vector_boosted={last_cycle.get('vector_boosted', 0)} "
                f"few_shot_examples={last_cycle.get('few_shot_examples', 0)} "
                f"omitted_for_retry={last_cycle.get('omitted_for_retry', 0)} "
                f"marked_seen={last_cycle['marked_seen']} llm_failed={last_cycle['llm_failed']}"
            )
        )

    return "\n".join(lines)


def _format_vip_senders(store: StateStore) -> str:
    rows = store.list_vip_senders()
    if not rows:
        return "No VIP senders configured. Use /vip add <email>"

    lines = ["VIP senders:"]
    for row in rows[:50]:
        display_name = str(row.get("display_name", "")).strip()
        sender_email = str(row.get("sender_email", "")).strip()
        if display_name:
            lines.append(f"- {sender_email} ({display_name})")
        else:
            lines.append(f"- {sender_email}")
    return "\n".join(lines)


def _set_archive_noise_enabled(config: dict[str, Any], enabled: bool) -> None:
    config.setdefault("gmail", {})["archive_noise"] = bool(enabled)
    save_config(config)


def _handle_set_command(text: str, config: dict[str, Any]) -> str:
    payload = _extract_command_payload(text)
    parts = payload.split()
    if len(parts) != 2 or parts[0].strip().lower() != "archive":
        return "Usage: /set archive on|off"

    value = parts[1].strip().lower()
    if value not in {"on", "off"}:
        return "Usage: /set archive on|off"

    enabled = value == "on"
    _set_archive_noise_enabled(config, enabled)
    return f"Archive for noise emails is now {'on' if enabled else 'off'}."


def _handle_vip_command(text: str, store: StateStore) -> str:
    payload = _extract_command_payload(text)
    if not payload:
        return "Usage: /vip add|list|remove"

    parts = payload.split(maxsplit=1)
    action = parts[0].strip().lower()
    argument = parts[1].strip() if len(parts) == 2 else ""

    if action == "list":
        return _format_vip_senders(store)

    if action not in {"add", "remove"} or not argument:
        return "Usage: /vip add <email>, /vip list, or /vip remove <email>"

    sender_email, display_name = _normalize_email_address(argument)
    if not sender_email:
        return "Usage: /vip add <email>, /vip list, or /vip remove <email>"

    if action == "add":
        store.add_vip_sender(sender_email, display_name)
        if display_name:
            return f"VIP sender added: {sender_email} ({display_name})"
        return f"VIP sender added: {sender_email}"

    deleted = store.remove_vip_sender(sender_email)
    return "VIP sender removed." if deleted else "VIP sender not found."


def _format_watch_rules(store: StateStore) -> str:
    rows = store.list_watch_rules(active_only=True)
    if not rows:
        return "No active watch rules. Add one with /watchFor <context> [boost]"

    lines = ["Active watch rules:"]
    for item in rows[:20]:
        lines.append(
            (f"- id={item['id']} context={item['context']} boost={float(item['boost']):.2f}")
        )
    return "\n".join(lines)


def _handle_watch_for(text: str, store: StateStore) -> str:
    parts = text.strip().split()
    if len(parts) < 2:
        return "Usage: /watchFor <context> [boost]"

    payload = text.strip().split(maxsplit=1)[1].strip()
    if not payload:
        return "Usage: /watchFor <context> [boost]"

    context = payload
    boost = 0.20
    payload_parts = payload.rsplit(" ", maxsplit=1)
    if len(payload_parts) == 2:
        maybe_boost = payload_parts[1].strip()
        try:
            boost_value = float(maybe_boost)
            if 0.0 <= boost_value <= 1.0:
                boost = boost_value
                context = payload_parts[0].strip()
        except ValueError:
            pass

    if not context:
        return "Usage: /watchFor <context> [boost]"

    rule_id = store.add_watch_rule(context=context, boost=boost)
    return f"Watch rule created: id={rule_id} context={context} boost={boost:.2f}"


def _parse_unwatch_command(text: str) -> int | None:
    parts = text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1].strip())
    except ValueError:
        return None


def _extract_command_payload(text: str) -> str:
    parts = text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return ""
    return parts[1].strip()


def _normalize_command(text: str) -> str:
    head = text.strip().split(maxsplit=1)[0].lower()
    return head.split("@", maxsplit=1)[0]
