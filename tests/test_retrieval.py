from __future__ import annotations

import unittest
from collections.abc import Sequence

from agentic_salmon.retrieval import SemanticRetriever


class ConceptEmbedding:
    model_name = "concept-test-model"

    def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    @staticmethod
    def _embed(text: str) -> list[float]:
        value = text.lower()
        return [
            float(any(term in value for term in ("thermometer", "temperature", "endpoint"))),
            float(any(term in value for term in ("image", "species", "identity"))),
            float(any(term in value for term in ("basket", "overfill", "circulation"))),
            float(any(term in value for term in ("storage", "cold-chain", "thaw"))),
        ]


class RetrievalTests(unittest.TestCase):
    def test_semantic_concept_ranks_temperature_guidance(self) -> None:
        retriever = SemanticRetriever(ConceptEmbedding())

        results = retriever.search("safe seafood endpoint measurement", top_k=2)

        self.assertIn(results[0].chunk_id, {"usda-air-fryer-temperature", "fda-seafood-cooking"})
        self.assertGreater(results[0].score, 0.0)
        self.assertEqual(64, len(results[0].content_sha256))

    def test_retriever_rejects_unbounded_top_k(self) -> None:
        retriever = SemanticRetriever(ConceptEmbedding())
        with self.assertRaisesRegex(ValueError, "top_k"):
            retriever.search("fish", top_k=99)

    def test_source_resolution_returns_integrity_hash(self) -> None:
        retriever = SemanticRetriever(ConceptEmbedding())
        source = retriever.get_source("usda-air-fryer-safety")
        self.assertEqual(64, len(source["content_sha256"]))


if __name__ == "__main__":
    unittest.main()
