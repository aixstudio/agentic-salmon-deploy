"""Read-only MCP server exposing the local semantic RAG capability."""

from __future__ import annotations

from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from mcp.server import MCPServer

from .retrieval import FastEmbedBackend, SemanticRetriever


SERVER_NAME = "agentic-salmon-knowledge"
try:
    SERVER_VERSION = version("agentic-salmon")
except PackageNotFoundError:
    SERVER_VERSION = "0+uninstalled"


@lru_cache(maxsize=1)
def default_retriever() -> SemanticRetriever:
    return SemanticRetriever(FastEmbedBackend())


def create_server(retriever: SemanticRetriever | None = None) -> MCPServer:
    server = MCPServer(
        name=SERVER_NAME,
        version=SERVER_VERSION,
        instructions="Read-only semantic retrieval over reviewed Agentic Salmon sources.",
    )

    def active_retriever() -> SemanticRetriever:
        return retriever or default_retriever()

    @server.tool()
    def search_knowledge(query: str, top_k: int = 3) -> dict[str, Any]:
        """Return semantically ranked reviewed chunks for a bounded query."""

        chunks = active_retriever().search(query=query, top_k=top_k)
        return {
            "query": query,
            "model": active_retriever().model_name,
            "chunks": [chunk.to_dict() for chunk in chunks],
        }

    @server.tool()
    def get_source(source_id: str) -> dict[str, str]:
        """Resolve one returned source identifier to reviewed metadata."""

        return active_retriever().get_source(source_id)

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
