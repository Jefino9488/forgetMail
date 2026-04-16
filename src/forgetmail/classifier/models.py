from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmailCandidate:
    message_id: str
    thread_id: str
    sender: str
    subject: str
    snippet: str


@dataclass
class EmailClassification:
    message_id: str
    important: bool
    score: float
    reason: str
