"""Small, governed ontology for the Agentic Salmon journey."""

from __future__ import annotations

from dataclasses import dataclass

from .models import EntityKind, RelationKind


@dataclass(frozen=True)
class RelationRule:
    subject_kind: EntityKind
    relation_kind: RelationKind
    object_kind: EntityKind


@dataclass(frozen=True)
class Ontology:
    name: str
    version: str
    entity_kinds: frozenset[EntityKind]
    relation_rules: frozenset[RelationRule]

    def permits(
        self,
        subject_kind: EntityKind,
        relation_kind: RelationKind,
        object_kind: EntityKind,
    ) -> bool:
        return RelationRule(subject_kind, relation_kind, object_kind) in self.relation_rules


SALMON_ONTOLOGY = Ontology(
    name="agentic-salmon-kitchen",
    version="1.0.0",
    entity_kinds=frozenset(EntityKind),
    relation_rules=frozenset(
        {
            RelationRule(
                EntityKind.FOOD_PORTION,
                RelationKind.LOCATED_IN,
                EntityKind.COOKING_EQUIPMENT,
            ),
            RelationRule(
                EntityKind.FOOD_PORTION,
                RelationKind.HAS_VISIBLE_FEATURE,
                EntityKind.OBSERVABLE_FEATURE,
            ),
        }
    ),
)
