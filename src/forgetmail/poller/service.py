from __future__ import annotations

import logging

from forgetmail.auth.google import get_credentials
from forgetmail.classifier import EmailCandidate
from forgetmail.gmail_client import GmailClient

from .parsing import _header_map


def list_recent_unread_message_ids(
    lookback_days: int,
    max_messages: int,
) -> list[str]:
    logging.debug("Poller: creating Gmail client")
    creds = get_credentials(allow_reauth=False)
    gmail = GmailClient(creds, timeout_seconds=30)

    query = f"is:unread newer_than:{lookback_days}d"
    logging.debug("Poller: listing messages with query='%s' max_results=%s", query, max_messages)
    items = gmail.list_messages(query=query, max_results=max_messages)
    logging.debug("Poller: API returned message stubs=%s", len(items))

    ids: list[str] = []
    for item in items:
        message_id = item.get("id")
        if isinstance(message_id, str) and message_id:
            ids.append(message_id)
    return ids


def fetch_message_candidates(message_ids: list[str]) -> list[EmailCandidate]:
    if not message_ids:
        return []

    logging.debug("Poller: creating Gmail client")
    creds = get_credentials(allow_reauth=False)
    gmail = GmailClient(creds, timeout_seconds=30)

    candidates: list[EmailCandidate] = []
    for message_id in message_ids:
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


def fetch_recent_unread_messages(
    lookback_days: int,
    max_messages: int,
) -> list[EmailCandidate]:
    ids = list_recent_unread_message_ids(lookback_days=lookback_days, max_messages=max_messages)
    return fetch_message_candidates(ids)


def mark_messages_read(message_ids: list[str]) -> set[str]:
    if not message_ids:
        return set()

    logging.debug("Poller: marking Gmail messages as read count=%s", len(message_ids))
    creds = get_credentials(allow_reauth=False)
    gmail = GmailClient(creds, timeout_seconds=30)

    marked: set[str] = set()
    for message_id in message_ids:
        try:
            gmail.modify_message_labels(message_id, remove_labels=["UNREAD"])
            marked.add(message_id)
        except Exception:
            logging.exception("Poller: failed to mark message as read message_id=%s", message_id)

    logging.debug("Poller: marked read successfully count=%s", len(marked))
    return marked
