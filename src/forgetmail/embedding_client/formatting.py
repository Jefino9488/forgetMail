from __future__ import annotations

from forgetmail.classifier import EmailCandidate


def candidate_to_embedding_text(candidate: EmailCandidate) -> str:
    sender = " ".join(candidate.sender.split())
    subject = " ".join(candidate.subject.split())
    snippet = " ".join(candidate.snippet.split())
    return f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}".strip()
