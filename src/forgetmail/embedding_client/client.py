from __future__ import annotations

from dataclasses import dataclass

import httpx


class EmbeddingError(RuntimeError):
    pass


@dataclass
class EmbeddingClient:
    provider: str
    model: str
    base_url: str
    timeout_seconds: int
    batch_size: int

    @classmethod
    def from_config(cls, config: dict) -> "EmbeddingClient":
        provider = str(config.get("provider", "ollama")).strip().lower()
        model = str(config.get("model", "")).strip()
        base_url = (
            str(config.get("base_url", "http://127.0.0.1:11434")).strip()
            or "http://127.0.0.1:11434"
        )
        timeout_seconds = int(config.get("timeout_seconds", 30))
        batch_size = max(1, int(config.get("batch_size", 32)))

        if not model:
            raise EmbeddingError("Embedding model is required.")

        return cls(
            provider=provider,
            model=model,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            batch_size=batch_size,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if self.provider != "ollama":
            raise EmbeddingError("Only local Ollama embeddings are supported in this phase.")

        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            chunk = texts[start : start + self.batch_size]
            vectors.extend(self._embed_with_ollama(chunk))

        if len(vectors) != len(texts):
            raise EmbeddingError(
                f"Embedding response mismatch: expected {len(texts)} vectors, got {len(vectors)}"
            )

        return vectors

    def _embed_with_ollama(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "model": self.model,
            "input": texts,
        }
        response = httpx.post(
            f"{self.base_url.rstrip('/')}/api/embed",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        data = response.json()
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list):
            raise EmbeddingError("Ollama embedding response missing 'embeddings' list.")

        normalized: list[list[float]] = []
        for item in embeddings:
            if not isinstance(item, list):
                raise EmbeddingError("Invalid embedding vector shape in response.")
            vector: list[float] = []
            for value in item:
                try:
                    vector.append(float(value))
                except (TypeError, ValueError) as exc:
                    raise EmbeddingError("Embedding vector contains non-numeric values.") from exc
            normalized.append(vector)

        return normalized
