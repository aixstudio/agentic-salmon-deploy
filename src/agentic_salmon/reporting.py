"""Write an ignored, reviewable Markdown run report."""

from __future__ import annotations

import json
from pathlib import Path

from .models import RunResult


def write_report(result: RunResult, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"agentic-salmon-{result.run_id}.md"
    stages = " → ".join(event.stage.value.upper() for event in result.events)
    lines = [
        "# Agentic Salmon Run",
        "",
        f"- Run ID: `{result.run_id}`",
        f"- Status: `{result.status}`",
        f"- Decision: `{result.decision.value}`",
        f"- Executed: {stages}",
        f"- Total measured node time: {result.total_duration_ms:.3f} ms",
        "- Token usage: N/A; reviewed fixture and deterministic agent contracts",
        "",
        "## Measured Node Timing",
        "",
        "| Agent | Duration (ms) |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {metric.stage.value} | {metric.duration_ms:.3f} |"
        for metric in result.metrics
    )
    lines.extend(
        [
            "",
            "## Public Trace",
            "",
            "```json",
            json.dumps(result.to_dict(), indent=2),
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
