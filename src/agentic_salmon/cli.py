"""Command-line runner for the Agentic Salmon demonstration."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .knowledge_port import McpKnowledgePort
from .models import HumanEvidence
from .perceive import PerceiveAgent
from .providers import ReviewedFixtureProvider
from .reason import ReasonAgent
from .reporting import write_report
from .workflow import AgenticSalmonWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the governed six-agent workflow with semantic RAG over MCP."
    )
    parser.add_argument("command", nargs="?", choices=("demo",), default="demo")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("examples/frozen-salmon-observation.json"),
    )
    parser.add_argument(
        "--input-image",
        type=Path,
        default=Path("docs/assets/salmon-pre-cook-input.jpeg"),
    )
    parser.add_argument(
        "--review",
        choices=("pending", "allow-bounded", "stop"),
        default="pending",
        help="Human response used to resume the Review interrupt.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt at Review and resume the same run until input is valid or stopped.",
    )
    parser.add_argument("--selected-hypothesis", default="fish")
    parser.add_argument("--storage-recollection")
    parser.add_argument("--odor-observation")
    parser.add_argument("--outcome")
    parser.add_argument("--feedback")
    parser.add_argument("--model-cache", type=Path)
    parser.add_argument("--report-directory", type=Path, default=Path("traces"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.model_cache is not None:
        os.environ["AGENTIC_SALMON_MODEL_CACHE"] = str(args.model_cache.resolve())

    provider = ReviewedFixtureProvider(args.fixture, args.input_image)
    knowledge = McpKnowledgePort(
        python_executable=sys.executable,
        working_directory=Path.cwd(),
    )
    workflow = AgenticSalmonWorkflow(
        PerceiveAgent(provider),
        ReasonAgent(knowledge),
    )
    if args.interactive and args.review != "pending":
        raise SystemExit("--interactive cannot be combined with --review")
    if args.interactive:
        result = workflow.run(outcome=args.outcome, feedback=args.feedback)
        while result.interrupt is not None:
            _display_interrupt(result.interrupt, result.run_id)
            result = workflow.resume(
                result.run_id,
                _prompt_review(result.interrupt),
            )
    else:
        result = workflow.run(
            _review_response(args),
            outcome=args.outcome,
            feedback=args.feedback,
        )
    report_path = write_report(result, args.report_directory)
    payload = result.to_dict()
    payload["local_report"] = str(report_path)
    print(json.dumps(payload, indent=2))
    return 0


def _review_response(args: argparse.Namespace) -> HumanEvidence | None:
    if args.review == "pending":
        return None
    if args.review == "stop":
        return HumanEvidence(
            selected_hypothesis=args.selected_hypothesis,
            concern_reported=True,
            authorizes_bounded_guidance=False,
            storage_recollection=args.storage_recollection,
            odor_observation=args.odor_observation,
        )
    return HumanEvidence(
        selected_hypothesis=args.selected_hypothesis,
        accepts_retained_unknowns=True,
        authorizes_bounded_guidance=True,
        storage_recollection=args.storage_recollection,
        odor_observation=args.odor_observation,
    )


def _display_interrupt(payload: dict[str, object], run_id: str) -> None:
    print(f"\nReview interrupt for run {run_id}")
    for message in payload.get("validation_messages", []):
        print(f"- {message}")
    print("Retained unknowns:")
    for item in payload.get("retained_unknowns", []):
        print(f"- {item}")
    print("Hypothesis choices:")
    for number, item in enumerate(_offered_hypotheses(payload), start=1):
        eligibility = (
            "action eligible"
            if item.get("action_eligible")
            else "not action eligible"
        )
        print(
            f"{number}) {item['label']} "
            f"[{item['status']}; {eligibility}] "
            f"(key: {item['hypothesis_id']})"
        )


def _prompt_review(payload: dict[str, object]) -> HumanEvidence:
    offered = _offered_hypotheses(payload)
    choice = input("Choose a number, hypothesis key, or 'stop': ").strip()
    if choice.lower() == "stop":
        return HumanEvidence(authorizes_bounded_guidance=False)
    selected = choice
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(offered):
            selected = str(offered[index]["hypothesis_id"])
    allowed = {
        str(item["hypothesis_id"])
        for item in offered
        if item.get("action_eligible") is True
    }
    if selected not in allowed:
        return HumanEvidence(selected_hypothesis=selected)
    accepts = _prompt_yes_no("Accept the displayed retained unknowns? [y/N]: ")
    authorizes = _prompt_yes_no("Authorize only bounded cited guidance? [y/N]: ")
    storage = input("Storage recollection (optional): ").strip() or None
    odor = input("Odor observation (optional): ").strip() or None
    return HumanEvidence(
        selected_hypothesis=selected,
        accepts_retained_unknowns=accepts,
        authorizes_bounded_guidance=authorizes,
        storage_recollection=storage,
        odor_observation=odor,
    )


def _prompt_yes_no(prompt: str) -> bool:
    return input(prompt).strip().lower() in {"y", "yes"}


def _offered_hypotheses(payload: dict[str, object]) -> list[dict[str, object]]:
    return [
        item
        for item in payload.get("offered_hypotheses", [])
        if isinstance(item, dict) and "hypothesis_id" in item
    ]
