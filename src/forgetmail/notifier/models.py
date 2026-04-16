from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SignalNotification:
    message_id: str
    thread_id: str
    sender: str
    subject: str
    reason: str
    score: float
