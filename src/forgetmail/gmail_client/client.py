from __future__ import annotations

import time
from typing import Any

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials


class GmailClient:
    def __init__(self, creds: Credentials, timeout_seconds: int = 30):
        self._session = AuthorizedSession(creds)
        self._timeout_seconds = timeout_seconds
        self._base = "https://gmail.googleapis.com/gmail/v1/users/me"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                response = self._session.request(
                    method,
                    f"{self._base}{path}",
                    params=params,
                    json=json_body,
                    timeout=self._timeout_seconds,
                )
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise RuntimeError("Unexpected Gmail API response shape.")
                return payload
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(attempt)

        raise RuntimeError(f"Gmail request failed after retries: {last_error}")

    def get_profile(self) -> dict[str, Any]:
        return self._request("GET", "/profile")

    def list_messages(self, query: str, max_results: int) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            "/messages",
            params={"q": query, "maxResults": max_results},
        )
        messages = payload.get("messages", [])
        if not isinstance(messages, list):
            return []
        return [item for item in messages if isinstance(item, dict)]

    def get_message_metadata(self, message_id: str) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/messages/{message_id}",
            params={
                "format": "metadata",
                "metadataHeaders": ["From", "Subject"],
            },
        )

    def get_message_full(self, message_id: str) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/messages/{message_id}",
            params={"format": "full"},
        )

    def modify_message_labels(
        self,
        message_id: str,
        *,
        add_labels: list[str] | None = None,
        remove_labels: list[str] | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/messages/{message_id}/modify",
            json_body={
                "addLabelIds": add_labels or [],
                "removeLabelIds": remove_labels or [],
            },
        )
