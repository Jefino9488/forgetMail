from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from forgetmail.classifier import EmailCandidate
from forgetmail.embedding_client import candidate_to_embedding_text


class VectorStoreError(RuntimeError):
    pass


@dataclass
class VectorStore:
    persist_path: Path
    collection_name: str

    def __post_init__(self) -> None:
        self.persist_path.mkdir(parents=True, exist_ok=True)

        try:
            import chromadb
        except Exception as exc:
            raise VectorStoreError("ChromaDB is not installed or unavailable.") from exc

        self._client = chromadb.PersistentClient(path=str(self.persist_path))
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "VectorStore":
        persist_path = Path(
            str(config.get("persist_path", "~/.config/forgetmail/chroma"))
        ).expanduser()
        collection_name = str(config.get("collection", "emails")).strip() or "emails"
        return cls(persist_path=persist_path, collection_name=collection_name)

    def upsert_email_candidates(
        self,
        candidates: list[EmailCandidate],
        embeddings: list[list[float]],
        *,
        source: str = "gmail_unread",
    ) -> int:
        if not candidates:
            return 0

        if len(candidates) != len(embeddings):
            raise VectorStoreError(
                f"Candidate/vector mismatch: candidates={len(candidates)} embeddings={len(embeddings)}"
            )

        now = datetime.now(timezone.utc).isoformat()
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for candidate in candidates:
            ids.append(candidate.message_id)
            documents.append(candidate_to_embedding_text(candidate))
            metadatas.append(
                {
                    "message_id": candidate.message_id,
                    "thread_id": candidate.thread_id,
                    "sender": candidate.sender,
                    "subject": candidate.subject,
                    "snippet": candidate.snippet,
                    "source": source,
                    "embedded_at": now,
                }
            )

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        return len(ids)

    def upsert_documents(
        self,
        *,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> int:
        if not ids:
            return 0
        if not (len(ids) == len(documents) == len(embeddings) == len(metadatas)):
            raise VectorStoreError(
                "Vector upsert input mismatch: "
                f"ids={len(ids)} docs={len(documents)} embeddings={len(embeddings)} metadatas={len(metadatas)}"
            )

        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(ids)

    def get_by_ids(self, ids: list[str]) -> dict[str, Any]:
        if not ids:
            return {"ids": [], "metadatas": [], "documents": []}

        return self._collection.get(ids=ids, include=["documents", "metadatas"])

    def update_classification_results(
        self,
        rows: list[tuple[str, str, str, str, int, float, str, str, str]],
    ) -> int:
        if not rows:
            return 0

        ids: list[str] = []
        metadatas: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        for row in rows:
            (
                message_id,
                _thread_id,
                _sender,
                _subject,
                important,
                score,
                reason,
                provider,
                model,
            ) = row
            ids.append(str(message_id))
            metadatas.append(
                {
                    "important": int(important),
                    "score": float(score),
                    "reason": str(reason),
                    "provider": str(provider),
                    "model": str(model),
                    "classified_at": now,
                }
            )

        self._collection.update(ids=ids, metadatas=metadatas)
        return len(ids)

    def query_similar(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._collection.query(
            query_embeddings=[query_embedding],
            n_results=max(1, int(top_k)),
            where=where,
        )

    def query_similar_by_embeddings(
        self,
        query_embeddings: list[list[float]],
        *,
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not query_embeddings:
            return {"ids": [], "metadatas": [], "distances": []}

        return self._collection.query(
            query_embeddings=query_embeddings,
            n_results=max(1, int(top_k)),
            where=where,
        )
