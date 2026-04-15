from __future__ import annotations

import json
from pathlib import Path

import httplib2
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from forgetmail.secrets import get_secret, set_secret

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.events",
]

GOOGLE_CREDS_KEY = "google_credentials_json"
DEFAULT_CLIENT_SECRET_PATH = Path.home() / ".config" / "forgetmail" / "client_secret.json"


class _TimeoutSession(requests.Session):
    def __init__(self, timeout_seconds: int):
        super().__init__()
        self._timeout_seconds = timeout_seconds

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self._timeout_seconds)
        return super().request(method, url, **kwargs)


def _load_cached_credentials() -> Credentials | None:
    raw = get_secret(GOOGLE_CREDS_KEY)
    if not raw:
        return None

    try:
        payload = json.loads(raw)
        return Credentials.from_authorized_user_info(payload, SCOPES)
    except Exception:
        return None


def _cache_credentials(creds: Credentials) -> None:
    if not set_secret(GOOGLE_CREDS_KEY, creds.to_json()):
        raise RuntimeError(
            "Could not store Google credentials in keyring. "
            "Set FORGETMAIL_GOOGLE_CREDENTIALS_JSON as an environment variable."
        )


def get_credentials(
    client_secret_path: Path | None = None,
    allow_reauth: bool = True,
    refresh_timeout_seconds: int = 12,
) -> Credentials:
    creds = _load_cached_credentials()

    if creds and creds.expired and creds.refresh_token:
        request = Request(session=_TimeoutSession(refresh_timeout_seconds))
        try:
            creds.refresh(request)
        except Exception as exc:
            if not allow_reauth:
                detail = str(exc).strip() or exc.__class__.__name__
                detail_lower = detail.lower()
                if (
                    "invalid_grant" in detail_lower
                    or "expired or revoked" in detail_lower
                    or "invalid refresh token" in detail_lower
                ):
                    raise RuntimeError(
                        "Cached Google refresh token is invalid or revoked. "
                        "Re-run forgetMail --onboard to re-authenticate Google."
                    ) from exc
                raise RuntimeError(
                    "Cached Google credentials could not be refreshed. "
                    f"Refresh error: {detail}"
                ) from exc
            creds = None
        else:
            _cache_credentials(creds)

    if creds and creds.valid:
        return creds

    if not allow_reauth:
        raise RuntimeError("No valid cached Google credentials. Run forgetMail --onboard.")

    if client_secret_path is None:
        client_secret_path = DEFAULT_CLIENT_SECRET_PATH

    client_secret_path = client_secret_path.expanduser().resolve()
    if not client_secret_path.exists():
        raise FileNotFoundError(f"client_secret.json not found at: {client_secret_path}")

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
    try:
        creds = flow.run_local_server(port=0, open_browser=True)
    except Exception:
        creds = flow.run_console()

    _cache_credentials(creds)
    return creds


def build_gmail_service(creds: Credentials, timeout_seconds: int = 25):
    authed_http = AuthorizedHttp(creds, http=httplib2.Http(timeout=timeout_seconds))
    return build("gmail", "v1", http=authed_http, cache_discovery=False)
