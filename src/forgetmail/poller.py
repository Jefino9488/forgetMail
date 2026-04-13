from __future__ import annotations

import logging

from forgetmail.auth.google import get_credentials
from forgetmail.classifier import EmailCandidate
from forgetmail.gmail_client import GmailClient


def _header_map(headers: list[dict[str, str]]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for item in headers:
        key = item.get("name")
        value = item.get("value")
        if isinstance(key, str) and isinstance(value, str):
            mapped[key.lower()] = value
    return mapped


def fetch_recent_unread_messages(
    lookback_days: int,
    max_messages: int,
) -> list[EmailCandidate]:
    logging.debug("Poller: creating Gmail client")
    creds = get_credentials(allow_reauth=False)
    gmail = GmailClient(creds, timeout_seconds=30)

    query = f"is:unread newer_than:{lookback_days}d"
    logging.debug("Poller: listing messages with query='%s' max_results=%s", query, max_messages)
    items = gmail.list_messages(query=query, max_results=max_messages)
    logging.debug("Poller: API returned message stubs=%s", len(items))

    candidates: list[EmailCandidate] = []
    for item in items:
        message_id = item.get("id")
        if not isinstance(message_id, str) or not message_id:
            continue

        logging.debug("Poller: fetching metadata for message_id=%s", message_id)
        full = gmail.get_message_metadata(message_id)
        payload = full.get("payload", {})
        headers = _header_map(payload.get("headers", []))

        candidates.append(
            EmailCandidate(
                message_id=message_id,
                thread_id=str(full.get("threadId", "")),
                sender=headers.get("from", "unknown"),
                subject=headers.get("subject", "(no subject)"),
                snippet=str(full.get("snippet", "")).strip(),
            )
        )

    logging.debug("Poller: constructed candidates=%s", len(candidates))
    return candidates
