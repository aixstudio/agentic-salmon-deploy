"""Perception provider seam used by the Perceive agent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

from .models import (
    AssertionSource,
    CandidateHypothesis,
    EntityKind,
    EntityMention,
    Observation,
    Perception,
    RelationKind,
    RelationshipMention,
)


class VisionProvider(Protocol):
    def perceive(self) -> Perception:
        """Return observable claims, explicit unknowns, and provenance."""


class ReviewedFixtureProvider:
    def __init__(self, fixture_path: Path, input_image: Path) -> None:
        self.fixture_path = fixture_path
        self.input_image = input_image

    def perceive(self) -> Perception:
        data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        _reject_unknown_keys(
            data,
            {
                "provenance",
                "input_image_sha256",
                "observations",
                "unknowns",
                "candidate_hypotheses",
                "entity_mentions",
                "relationship_mentions",
            },
            "fixture",
        )
        actual_sha256 = _sha256(self.input_image)
        expected_sha256 = data["input_image_sha256"]
        if actual_sha256 != expected_sha256:
            raise ValueError(
                "input image does not match the reviewed fixture: "
                f"expected {expected_sha256}, got {actual_sha256}"
            )
        observations = tuple(
            Observation(
                observation_id=item["observation_id"],
                claim=item["claim"],
                source=item["source"],
            )
            for item in _validated_items(
                data["observations"],
                {"observation_id", "claim", "source"},
                "observation",
            )
        )
        candidate_hypotheses = tuple(
            CandidateHypothesis(
                hypothesis_id=item["hypothesis_id"],
                label=item["label"],
                source_kind=AssertionSource(item["source_kind"]),
                claim=item["claim"],
                supporting_observation_ids=tuple(
                    item.get("supporting_observation_ids", [])
                ),
            )
            for item in _validated_items(
                data.get("candidate_hypotheses", []),
                {
                    "hypothesis_id",
                    "label",
                    "source_kind",
                    "claim",
                    "supporting_observation_ids",
                },
                "candidate hypothesis",
            )
        )
        entity_mentions = tuple(
            EntityMention(
                mention_id=item["mention_id"],
                entity_kind=EntityKind(item["entity_kind"]),
                label=item["label"],
                evidence_claim=item["evidence_claim"],
            )
            for item in _validated_items(
                data.get("entity_mentions", []),
                {"mention_id", "entity_kind", "label", "evidence_claim"},
                "entity mention",
            )
        )
        relationship_mentions = tuple(
            RelationshipMention(
                subject_mention_id=item["subject_mention_id"],
                relation_kind=RelationKind(item["relation_kind"]),
                object_mention_id=item["object_mention_id"],
                evidence_claim=item["evidence_claim"],
            )
            for item in _validated_items(
                data.get("relationship_mentions", []),
                {
                    "subject_mention_id",
                    "relation_kind",
                    "object_mention_id",
                    "evidence_claim",
                },
                "relationship mention",
            )
        )
        return Perception(
            observations=observations,
            unknowns=tuple(data["unknowns"]),
            provenance=data["provenance"],
            input_image_sha256=actual_sha256,
            candidate_hypotheses=candidate_hypotheses,
            entity_mentions=entity_mentions,
            relationship_mentions=relationship_mentions,
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validated_items(
    items: list[dict[str, object]],
    allowed: set[str],
    label: str,
) -> list[dict[str, object]]:
    for index, item in enumerate(items):
        _reject_unknown_keys(item, allowed, f"{label} {index}")
    return items


def _reject_unknown_keys(
    value: dict[str, object],
    allowed: set[str],
    label: str,
) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"unsupported {label} fields: {sorted(unknown)}")
