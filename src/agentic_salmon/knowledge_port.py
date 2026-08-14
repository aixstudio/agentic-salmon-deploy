"""Typed knowledge port and MCP-backed adapter used by Reason."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

from mcp import Client, StdioServerParameters, stdio_client
from mcp.server import MCPServer

from .models import KnowledgeResult, McpCall, RetrievedChunk


class KnowledgePort(Protocol):
    async def search(self, query: str, top_k: int = 3) -> KnowledgeResult:
        """Retrieve semantic context for Reason."""


@dataclass
class McpKnowledgePort:
    """Invoke the semantic retriever through an actual MCP boundary."""

    server: MCPServer | None = None
    python_executable: str = sys.executable
    working_directory: Path | None = None

    async def search(self, query: str, top_k: int = 3) -> KnowledgeResult:
        started = perf_counter()
        target: MCPServer | Any
        if self.server is not None:
            target = self.server
        else:
            extra_env = {
                key: os.environ[key]
                for key in (
                    "AGENTIC_SALMON_MODEL_CACHE",
                    "HF_HOME",
                    "HF_HUB_OFFLINE",
                )
                if key in os.environ
            }
            parameters = StdioServerParameters(
                command=self.python_executable,
                args=["-m", "agentic_salmon.mcp_server"],
                cwd=self.working_directory,
                env=extra_env,
            )
            target = stdio_client(parameters)

        async with Client(target, raise_exceptions=True) as client:
            response = await client.call_tool(
                "search_knowledge",
                {"query": query, "top_k": top_k},
            )
            if response.is_error:
                raise RuntimeError("MCP search_knowledge returned an error")
            payload = _unwrap(response.structured_content)
            server_info = client.server_info
            server_name = server_info.name if server_info is not None else "unknown"
            server_version = server_info.version if server_info is not None else "unknown"
            protocol_version = client.protocol_version

        duration_ms = round((perf_counter() - started) * 1000, 3)
        return KnowledgeResult(
            query=str(payload["query"]),
            model=str(payload["model"]),
            chunks=tuple(RetrievedChunk(**item) for item in payload["chunks"]),
            mcp_call=McpCall(
                server_name=server_name,
                server_version=server_version,
                protocol_version=protocol_version,
                tool_name="search_knowledge",
                duration_ms=duration_ms,
                success=True,
            ),
        )


def _unwrap(value: dict[str, Any] | None) -> dict[str, Any]:
    if value is None:
        raise RuntimeError("MCP tool did not return structured content")
    result = value.get("result")
    if isinstance(result, dict):
        return result
    return value
