"""Reason agent: evaluate hypotheses with optional semantic RAG context."""

from __future__ import annotations

from .knowledge_port import KnowledgePort
from .models import (
    AssertionSource,
    CandidateHypothesis,
    ConnectedEvent,
    EntityKind,
    Hypothesis,
    HypothesisStatus,
    Observation,
    Perception,
    ReasonResult,
)


class ReasonAgent:
    def __init__(self, knowledge: KnowledgePort) -> None:
        self.knowledge = knowledge

    async def reason(
        self,
        perception: Perception,
        connected: ConnectedEvent,
    ) -> ReasonResult:
        query = _build_query(perception, connected)
        knowledge = await self.knowledge.search(query, top_k=3)
        if not knowledge.chunks:
            raise ValueError("Reason requested RAG context but retrieval returned no chunks")

        observations = {
            item.observation_id: item for item in perception.observations
        }
        limiting_chunks = tuple(
            chunk.chunk_id
            for chunk in knowledge.chunks
            if "cannot verify species" in chunk.text.lower()
            or "image without original packaging" in chunk.text.lower()
        )
        hypotheses = tuple(
            _evaluate_candidate(candidate, observations, limiting_chunks)
            for candidate in perception.candidate_hypotheses
        )
        if not hypotheses:
            raise ValueError("Reason requires source-bound candidate hypotheses")
        return ReasonResult(
            query=query,
            hypotheses=hypotheses,
            retained_unknowns=perception.unknowns,
            proposed_action=(
                "Ask the human to select a working hypothesis, accept the retained "
                "unknowns, and explicitly authorize only bounded guidance grounded "
                "in the retrieved sources."
            ),
            knowledge=knowledge,
        )


def _build_query(perception: Perception, connected: ConnectedEvent) -> str:
    entity_labels = ", ".join(
        entity.label
        for entity in connected.entities
        if entity.entity_kind
        in {EntityKind.FOOD_PORTION, EntityKind.COOKING_EQUIPMENT}
    )
    unknowns = ", ".join(perception.unknowns)
    candidates = ", ".join(
        item.label for item in perception.candidate_hypotheses
    )
    return (
        "semantic guidance for unidentified seasoned food portions with a visible "
        "skin-like surface in an air fryer; "
        f"scene entities: {entity_labels}; retained unknowns: {unknowns}; "
        f"source-bound candidate hypotheses: {candidates}; "
        "food thermometer, bounded guidance, image evidence limits"
    )


def _evaluate_candidate(
    candidate: CandidateHypothesis,
    observations: dict[str, Observation],
    limiting_chunks: tuple[str, ...],
) -> Hypothesis:
    supporting = tuple(
        observations[item]
        for item in candidate.supporting_observation_ids
        if item in observations
    )
    if candidate.source_kind is AssertionSource.MODEL_ASSERTION:
        status = HypothesisStatus.PLAUSIBLE if supporting else HypothesisStatus.UNKNOWN
    else:
        status = HypothesisStatus.SUPPORTED if supporting else HypothesisStatus.UNKNOWN
    evidence_claims = (candidate.claim,) + tuple(
        item.claim for item in supporting
    )
    evidence_ids = (f"candidate:{candidate.hypothesis_id}",) + tuple(
        item.observation_id for item in supporting
    )
    return Hypothesis(
        hypothesis_id=candidate.hypothesis_id,
        name=candidate.label,
        status=status,
        evidence_claims=evidence_claims,
        evidence_ids=evidence_ids,
        limiting_chunk_ids=(
            limiting_chunks
            if candidate.source_kind is AssertionSource.MODEL_ASSERTION
            else ()
        ),
    )
