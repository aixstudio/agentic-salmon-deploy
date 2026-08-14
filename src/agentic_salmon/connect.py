"""Connect agent: resolve mentions and assemble one ontology-valid event."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import (
    ConnectedEvent,
    EntityKind,
    EntityMention,
    Perception,
    ResolvedEntity,
    ResolvedRelationship,
)
from .ontology import Ontology


class OntologyViolation(ValueError):
    """Raised when perceived mentions cannot form a valid instance graph."""


@dataclass
class _EntityAccumulator:
    kind: EntityKind
    label: str
    evidence: set[str] = field(default_factory=set)


class ConnectAgent:
    def __init__(self, ontology: Ontology) -> None:
        self.ontology = ontology

    def connect(self, perception: Perception) -> ConnectedEvent:
        mentions_by_id: dict[str, EntityMention] = {}
        entities_by_id: dict[str, _EntityAccumulator] = {}
        canonical_by_mention: dict[str, str] = {}
        kind_counts: dict[EntityKind, int] = {}

        for mention in perception.entity_mentions:
            if mention.mention_id in mentions_by_id:
                raise OntologyViolation(f"duplicate mention id: {mention.mention_id}")
            if mention.entity_kind not in self.ontology.entity_kinds:
                raise OntologyViolation(f"unknown entity kind: {mention.entity_kind}")
            mentions_by_id[mention.mention_id] = mention

            if mention.entity_kind is EntityKind.FOOD_PORTION:
                # This journey contains one observed collection of food portions.
                # Applying that event-scoped resolution policy is Connect's work.
                canonical_id = "food_portions_1"
            else:
                kind_counts[mention.entity_kind] = (
                    kind_counts.get(mention.entity_kind, 0) + 1
                )
                canonical_id = (
                    f"{mention.entity_kind.value}_{kind_counts[mention.entity_kind]}"
                )
            canonical_by_mention[mention.mention_id] = canonical_id

            existing = entities_by_id.get(canonical_id)
            if existing is None:
                entities_by_id[canonical_id] = _EntityAccumulator(
                    kind=mention.entity_kind,
                    label=mention.label,
                    evidence={mention.evidence_claim},
                )
            else:
                if existing.kind is not mention.entity_kind:
                    raise OntologyViolation(
                        f"canonical entity {canonical_id} has conflicting kinds"
                    )
                existing.evidence.add(mention.evidence_claim)

        relationships: list[ResolvedRelationship] = []
        for mention in perception.relationship_mentions:
            try:
                subject = mentions_by_id[mention.subject_mention_id]
                object_ = mentions_by_id[mention.object_mention_id]
            except KeyError as error:
                raise OntologyViolation(
                    f"relationship references unknown mention: {error.args[0]}"
                ) from error
            if not self.ontology.permits(
                subject.entity_kind,
                mention.relation_kind,
                object_.entity_kind,
            ):
                raise OntologyViolation(
                    "ontology rejects relationship: "
                    f"{subject.entity_kind.value} {mention.relation_kind.value} "
                    f"{object_.entity_kind.value}"
                )
            relationships.append(
                ResolvedRelationship(
                    subject_id=canonical_by_mention[subject.mention_id],
                    relation_kind=mention.relation_kind,
                    object_id=canonical_by_mention[object_.mention_id],
                    evidence_claim=mention.evidence_claim,
                )
            )

        entities = tuple(
            ResolvedEntity(
                entity_id=entity_id,
                entity_kind=value.kind,
                label=value.label,
                evidence_claims=tuple(sorted(value.evidence)),
            )
            for entity_id, value in sorted(entities_by_id.items())
        )
        event_suffix = (
            perception.input_image_sha256[:12]
            if perception.input_image_sha256 is not None
            else "unbound"
        )
        return ConnectedEvent(
            event_id=f"food-preparation-assessment:{event_suffix}",
            event_type="food_preparation_assessment",
            ontology_name=self.ontology.name,
            ontology_version=self.ontology.version,
            entities=entities,
            relationships=tuple(
                sorted(
                    relationships,
                    key=lambda item: (
                        item.subject_id,
                        item.relation_kind.value,
                        item.object_id,
                    ),
                )
            ),
        )
