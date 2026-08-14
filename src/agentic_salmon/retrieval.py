"""Small dense semantic retriever used behind the MCP knowledge server."""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Protocol, Sequence

from .models import RetrievedChunk


DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


class EmbeddingBackend(Protocol):
    model_name: str

    def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed corpus passages."""

    def embed_query(self, text: str) -> list[float]:
        """Embed one retrieval query."""


class FastEmbedBackend:
    """Dense ONNX embeddings without a vector database or hosted service."""

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        from fastembed import TextEmbedding

        cache_dir = os.environ.get("AGENTIC_SALMON_MODEL_CACHE")
        self.model_name = model_name
        self._model = TextEmbedding(
            model_name=model_name,
            cache_dir=cache_dir,
            threads=2,
        )

    def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.passage_embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.query_embed(text))).tolist()


@dataclass(frozen=True)
class _IndexedChunk:
    chunk: RetrievedChunk
    vector: tuple[float, ...]


class SemanticRetriever:
    """Embed a reviewed corpus in memory and rank by cosine similarity."""

    def __init__(
        self,
        backend: EmbeddingBackend,
        corpus_path: Path | None = None,
    ) -> None:
        self.backend = backend
        self.corpus_path = corpus_path or Path(
            str(files("agentic_salmon.knowledge").joinpath("corpus.json"))
        )
        data = json.loads(self.corpus_path.read_text(encoding="utf-8"))
        raw_chunks: list[RetrievedChunk] = []
        for source in data["sources"]:
            for item in source["chunks"]:
                text = item["text"]
                raw_chunks.append(
                    RetrievedChunk(
                        chunk_id=item["chunk_id"],
                        source_id=source["source_id"],
                        title=source["title"],
                        publisher=source["publisher"],
                        url=source["url"],
                        text=text,
                        score=0.0,
                        content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    )
                )
        vectors = backend.embed_passages([item.text for item in raw_chunks])
        if len(vectors) != len(raw_chunks):
            raise ValueError("embedding backend returned the wrong passage count")
        self._chunks = tuple(
            _IndexedChunk(chunk=chunk, vector=tuple(vector))
            for chunk, vector in zip(raw_chunks, vectors, strict=True)
        )

    @property
    def model_name(self) -> str:
        return self.backend.model_name

    def search(self, query: str, top_k: int = 3) -> tuple[RetrievedChunk, ...]:
        normalized = query.strip()
        if not normalized:
            raise ValueError("query must not be empty")
        if not 1 <= top_k <= 5:
            raise ValueError("top_k must be between 1 and 5")
        query_vector = self.backend.embed_query(normalized)
        ranked = sorted(
            (
                (
                    _cosine_similarity(query_vector, item.vector),
                    item.chunk,
                )
                for item in self._chunks
            ),
            key=lambda item: (-item[0], item[1].chunk_id),
        )[:top_k]
        return tuple(
            RetrievedChunk(
                **{
                    **chunk.to_dict(),
                    "score": round(float(score), 6),
                }
            )
            for score, chunk in ranked
        )

    def get_source(self, source_id: str) -> dict[str, str]:
        matches = [item.chunk for item in self._chunks if item.chunk.source_id == source_id]
        if not matches:
            raise ValueError(f"unknown source_id: {source_id}")
        source_hash = hashlib.sha256(
            "".join(sorted(item.content_sha256 for item in matches)).encode("ascii")
        ).hexdigest()
        first = matches[0]
        return {
            "source_id": first.source_id,
            "title": first.title,
            "publisher": first.publisher,
            "url": first.url,
            "content_sha256": source_hash,
        }


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions do not match")
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)
