"""Command-line entrypoint for the Agentic Salmon demonstration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import HumanEvidence
from .providers import ReviewedFixtureProvider
from .workflow import AgenticSalmonWorkflow


def _optional_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value == "yes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Demonstrate a controlled agentic loop with explicit human evidence."
    )
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--input-image", type=Path, required=True)
    parser.add_argument("--label-identified", choices=("yes", "no"))
    parser.add_argument("--remained-frozen", choices=("yes", "no"))
    parser.add_argument("--odor-normal", choices=("yes", "no"))
    parser.add_argument("--feedback")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    provider = ReviewedFixtureProvider(args.fixture, args.input_image)
    workflow = AgenticSalmonWorkflow(provider)
    result = workflow.run(
        HumanEvidence(
            label_identified=_optional_bool(args.label_identified),
            remained_frozen=_optional_bool(args.remained_frozen),
            odor_normal=_optional_bool(args.odor_normal),
        ),
        feedback=args.feedback,
    )
    print(json.dumps(result.to_dict(), indent=2))
    return 0
