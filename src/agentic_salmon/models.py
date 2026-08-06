"""Typed public state for the controlled workflow.

The public event model records evidence and decisions, never hidden reasoning.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Stage(StrEnum):
    PERCEIVE = "perceive"
    REASON = "reason"
    REVIEW = "review"
    ACT = "act"
    LEARN = "learn"


class GateDecision(StrEnum):
    ASK = "ask"
    ALLOW = "allow"
    STOP = "stop"


@dataclass(frozen=True)
class Observation:
    claim: str
    confidence: float
    source: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass(frozen=True)
class Perception:
    observations: tuple[Observation, ...]
    unknowns: tuple[str, ...]
    provenance: str
    input_image_sha256: str | None = None


@dataclass(frozen=True)
class HumanEvidence:
    label_identified: bool | None = None
    remained_frozen: bool | None = None
    odor_normal: bool | None = None


@dataclass(frozen=True)
class ReviewResult:
    decision: GateDecision
    reasons: tuple[str, ...]
    missing: tuple[str, ...] = ()


@dataclass(frozen=True)
class PublicEvent:
    sequence: int
    stage: Stage
    summary: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["stage"] = self.stage.value
        return value


@dataclass(frozen=True)
class RunResult:
    decision: GateDecision
    guidance: str | None
    events: tuple[PublicEvent, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "guidance": self.guidance,
            "events": [event.to_dict() for event in self.events],
        }
