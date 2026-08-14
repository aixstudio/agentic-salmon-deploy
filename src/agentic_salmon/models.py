"""Typed public contracts for the Agentic Salmon workflow.

The public models expose evidence, decisions, citations, and measured telemetry.
They never expose hidden reasoning or provider prompts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from enum import StrEnum
from typing import Any


class Stage(StrEnum):
    PERCEIVE = "perceive"
    CONNECT = "connect"
    REASON = "reason"
    REVIEW = "review"
    ACT = "act"
    LEARN = "learn"


class GateDecision(StrEnum):
    ASK = "ask"
    ALLOW_BOUNDED = "allow_bounded"
    STOP = "stop"


class HypothesisStatus(StrEnum):
    SUPPORTED = "supported"
    PLAUSIBLE = "plausible"
    UNKNOWN = "unknown"


class AssertionSource(StrEnum):
    HUMAN_HYPOTHESIS = "human_hypothesis"
    MODEL_ASSERTION = "model_assertion"


class EntityKind(StrEnum):
    FOOD_PORTION = "food_portion"
    COOKING_EQUIPMENT = "cooking_equipment"
    OBSERVABLE_FEATURE = "observable_feature"


class RelationKind(StrEnum):
    LOCATED_IN = "located_in"
    HAS_VISIBLE_FEATURE = "has_visible_feature"


@dataclass(frozen=True)
class Observation:
    observation_id: str
    claim: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateHypothesis:
    hypothesis_id: str
    label: str
    source_kind: AssertionSource
    claim: str
    supporting_observation_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["source_kind"] = self.source_kind.value
        value["supporting_observation_ids"] = list(self.supporting_observation_ids)
        return value


@dataclass(frozen=True)
class EntityMention:
    mention_id: str
    entity_kind: EntityKind
    label: str
    evidence_claim: str


@dataclass(frozen=True)
class RelationshipMention:
    subject_mention_id: str
    relation_kind: RelationKind
    object_mention_id: str
    evidence_claim: str


@dataclass(frozen=True)
class Perception:
    observations: tuple[Observation, ...]
    unknowns: tuple[str, ...]
    provenance: str
    input_image_sha256: str | None = None
    candidate_hypotheses: tuple[CandidateHypothesis, ...] = ()
    entity_mentions: tuple[EntityMention, ...] = ()
    relationship_mentions: tuple[RelationshipMention, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "observations": [item.to_dict() for item in self.observations],
            "unknowns": list(self.unknowns),
            "provenance": self.provenance,
            "input_image_sha256": self.input_image_sha256,
            "candidate_hypotheses": [
                item.to_dict() for item in self.candidate_hypotheses
            ],
            "entity_mentions": [
                {
                    **asdict(item),
                    "entity_kind": item.entity_kind.value,
                }
                for item in self.entity_mentions
            ],
            "relationship_mentions": [
                {
                    **asdict(item),
                    "relation_kind": item.relation_kind.value,
                }
                for item in self.relationship_mentions
            ],
        }


@dataclass(frozen=True)
class ResolvedEntity:
    entity_id: str
    entity_kind: EntityKind
    label: str
    evidence_claims: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_kind": self.entity_kind.value,
            "label": self.label,
            "evidence_claims": list(self.evidence_claims),
        }


@dataclass(frozen=True)
class ResolvedRelationship:
    subject_id: str
    relation_kind: RelationKind
    object_id: str
    evidence_claim: str

    def to_dict(self) -> dict[str, str]:
        return {
            "subject_id": self.subject_id,
            "relation_kind": self.relation_kind.value,
            "object_id": self.object_id,
            "evidence_claim": self.evidence_claim,
        }


@dataclass(frozen=True)
class ConnectedEvent:
    event_id: str
    event_type: str
    ontology_name: str
    ontology_version: str
    entities: tuple[ResolvedEntity, ...]
    relationships: tuple[ResolvedRelationship, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "ontology": {
                "name": self.ontology_name,
                "version": self.ontology_version,
            },
            "entities": [entity.to_dict() for entity in self.entities],
            "relationships": [relationship.to_dict() for relationship in self.relationships],
        }


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    source_id: str
    title: str
    publisher: str
    url: str
    text: str
    score: float
    content_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class McpCall:
    server_name: str
    server_version: str
    protocol_version: str
    tool_name: str
    duration_ms: float
    success: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeResult:
    query: str
    model: str
    chunks: tuple[RetrievedChunk, ...]
    mcp_call: McpCall

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "model": self.model,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "mcp_call": self.mcp_call.to_dict(),
        }


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    name: str
    status: HypothesisStatus
    evidence_claims: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    supporting_chunk_ids: tuple[str, ...] = ()
    limiting_chunk_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "name": self.name,
            "status": self.status.value,
            "evidence_claims": list(self.evidence_claims),
            "evidence_ids": list(self.evidence_ids),
            "supporting_chunk_ids": list(self.supporting_chunk_ids),
            "limiting_chunk_ids": list(self.limiting_chunk_ids),
        }


@dataclass(frozen=True)
class ReasonResult:
    query: str
    hypotheses: tuple[Hypothesis, ...]
    retained_unknowns: tuple[str, ...]
    proposed_action: str
    knowledge: KnowledgeResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "retained_unknowns": list(self.retained_unknowns),
            "proposed_action": self.proposed_action,
            "knowledge": self.knowledge.to_dict(),
        }


@dataclass(frozen=True)
class HumanEvidence:
    selected_hypothesis: str | None = None
    accepts_retained_unknowns: bool | None = None
    authorizes_bounded_guidance: bool | None = None
    concern_reported: bool = False
    storage_recollection: str | None = None
    odor_observation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> HumanEvidence:
        allowed = {item.name for item in fields(cls)}
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unsupported human evidence fields: {sorted(unknown)}")
        return cls(**value)


@dataclass(frozen=True)
class ReviewResult:
    decision: GateDecision
    reasons: tuple[str, ...]
    retained_unknowns: tuple[str, ...]
    selected_hypothesis: str | None = None
    resolved_unknowns: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "retained_unknowns": list(self.retained_unknowns),
            "selected_hypothesis": self.selected_hypothesis,
            "resolved_unknowns": list(self.resolved_unknowns),
        }


@dataclass(frozen=True)
class ActionResult:
    guidance: str
    authority: str
    citation_chunk_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "guidance": self.guidance,
            "authority": self.authority,
            "citation_chunk_ids": list(self.citation_chunk_ids),
        }


@dataclass(frozen=True)
class LearnResult:
    outcome: str | None
    preference_feedback: str | None
    policy_effect: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NodeMetric:
    stage: Stage
    started_at: str
    ended_at: str
    duration_ms: float

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["stage"] = self.stage.value
        return value


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
    run_id: str
    status: str
    decision: GateDecision
    guidance: str | None
    events: tuple[PublicEvent, ...]
    metrics: tuple[NodeMetric, ...]
    interrupt: dict[str, Any] | None = None

    @property
    def total_duration_ms(self) -> float:
        return round(sum(metric.duration_ms for metric in self.metrics), 3)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "decision": self.decision.value,
            "guidance": self.guidance,
            "interrupt": self.interrupt,
            "telemetry": {
                "total_duration_ms": self.total_duration_ms,
                "token_usage": None,
                "token_usage_note": (
                    "N/A; reviewed perception fixture and deterministic agent contracts"
                ),
            },
            "events": [event.to_dict() for event in self.events],
            "metrics": [metric.to_dict() for metric in self.metrics],
        }
