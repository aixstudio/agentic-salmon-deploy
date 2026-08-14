from __future__ import annotations

import asyncio
import unittest
from collections.abc import Sequence
from importlib.metadata import version

from mcp import Client

from agentic_salmon.knowledge_port import McpKnowledgePort
from agentic_salmon.mcp_server import SERVER_NAME, SERVER_VERSION, create_server
from agentic_salmon.retrieval import SemanticRetriever


class ConceptEmbedding:
    model_name = "mcp-concept-test-model"

    def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    @staticmethod
    def _embed(text: str) -> list[float]:
        value = text.lower()
        return [
            float("temperature" in value or "thermometer" in value),
            float("identity" in value or "species" in value),
        ]


class McpIntegrationTests(unittest.TestCase):
    def test_server_version_comes_from_package_metadata(self) -> None:
        self.assertEqual(version("agentic-salmon"), SERVER_VERSION)

    def test_real_mcp_client_server_returns_structured_semantic_results(self) -> None:
        retriever = SemanticRetriever(ConceptEmbedding())
        server = create_server(retriever)
        port = McpKnowledgePort(server=server)

        result = asyncio.run(port.search("fish temperature measurement", top_k=2))

        self.assertEqual(SERVER_NAME, result.mcp_call.server_name)
        self.assertEqual("search_knowledge", result.mcp_call.tool_name)
        self.assertTrue(result.mcp_call.success)
        self.assertEqual("mcp-concept-test-model", result.model)
        self.assertEqual(2, len(result.chunks))

    def test_real_mcp_get_source_resolves_reviewed_metadata(self) -> None:
        server = create_server(SemanticRetriever(ConceptEmbedding()))

        async def call_tool() -> dict[str, object]:
            async with Client(server, raise_exceptions=True) as client:
                response = await client.call_tool(
                    "get_source",
                    {"source_id": "usda-air-fryer-safety"},
                )
                payload = response.structured_content or {}
                result = payload.get("result", payload)
                return result if isinstance(result, dict) else {}

        result = asyncio.run(call_tool())

        self.assertEqual("USDA Food Safety and Inspection Service", result["publisher"])
        self.assertEqual(64, len(str(result["content_sha256"])))


if __name__ == "__main__":
    unittest.main()
