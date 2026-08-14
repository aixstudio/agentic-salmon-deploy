from __future__ import annotations

import asyncio
import unittest

from agentic_salmon.act import ActAgent
from agentic_salmon.connect import ConnectAgent, OntologyViolation
from agentic_salmon.guard import GuardPolicy
from agentic_salmon.learn import LearnAgent
from agentic_salmon.models import (
    ActionResult,
    AssertionSource,
    CandidateHypothesis,
    ConnectedEvent,
    EntityKind,
    EntityMention,
    GateDecision,
    HumanEvidence,
    Hypothesis,
    HypothesisStatus,
    KnowledgeResult,
    McpCall,
    Observation,
    Perception,
    ReasonResult,
    RelationKind,
    RelationshipMention,
    RetrievedChunk,
    ReviewResult,
    Stage,
)
from agentic_salmon.ontology import SALMON_ONTOLOGY
from agentic_salmon.perceive import PerceiveAgent
from agentic_salmon.reason import ReasonAgent
from agentic_salmon.review import ReviewAgent


class EmptyProvider:
    def perceive(self) -> Perception:
        return Perception(observations=(), unknowns=(), provenance="")


class EmptyKnowledge:
    async def search(self, query: str, top_k: int = 3) -> KnowledgeResult:
        return KnowledgeResult(
            query=query,
            model="empty-test-model",
            chunks=(),
            mcp_call=McpCall("test", "1", "test", "search_knowledge", 0.1, True),
        )


def perception() -> Perception:
    return Perception(
        observations=(Observation("skin", "A skin-like surface is visible.", "fixture"),),
        unknowns=("identity",),
        provenance="fixture",
        candidate_hypotheses=(
            CandidateHypothesis(
                "fish",
                "fish",
                AssertionSource.HUMAN_HYPOTHESIS,
                "The surface supports a fish hypothesis.",
                ("skin",),
            ),
        ),
        entity_mentions=(
            EntityMention("food", EntityKind.FOOD_PORTION, "food", "visible"),
            EntityMention(
                "food_feature_subject",
                EntityKind.FOOD_PORTION,
                "portion with skin-like surface",
                "surface visible",
            ),
            EntityMention(
                "basket",
                EntityKind.COOKING_EQUIPMENT,
                "basket",
                "visible",
            ),
        ),
        relationship_mentions=(
            RelationshipMention("food", RelationKind.LOCATED_IN, "basket", "visible"),
        ),
    )


def reason_result() -> ReasonResult:
    chunk = RetrievedChunk(
        "chunk",
        "source",
        "title",
        "publisher",
        "https://example.test",
        "fish thermometer 145 degrees",
        0.9,
        "c" * 64,
    )
    return ReasonResult(
        query="query",
        hypotheses=(
            Hypothesis("fish", "fish", HypothesisStatus.SUPPORTED, ("skin",)),
        ),
        retained_unknowns=("identity",),
        proposed_action="review",
        knowledge=KnowledgeResult(
            "query",
            "model",
            (chunk,),
            McpCall("server", "1", "p", "search_knowledge", 1.0, True),
        ),
    )


class AgentContractTests(unittest.TestCase):
    def test_perceive_rejects_missing_evidence_contract(self) -> None:
        with self.assertRaisesRegex(ValueError, "provenance"):
            PerceiveAgent(EmptyProvider()).perceive()

    def test_connect_resolves_event(self) -> None:
        connected = ConnectAgent(SALMON_ONTOLOGY).connect(perception())
        self.assertEqual("located_in", connected.relationships[0].relation_kind.value)
        food_entities = [
            item
            for item in connected.entities
            if item.entity_kind is EntityKind.FOOD_PORTION
        ]
        self.assertEqual(1, len(food_entities))
        self.assertEqual(
            "food_portions_1",
            food_entities[0].entity_id,
        )

    def test_connect_rejects_invalid_relationship(self) -> None:
        value = perception()
        invalid = Perception(
            observations=value.observations,
            unknowns=value.unknowns,
            provenance=value.provenance,
            entity_mentions=value.entity_mentions,
            relationship_mentions=(
                RelationshipMention(
                    "food",
                    RelationKind.HAS_VISIBLE_FEATURE,
                    "basket",
                    "invalid",
                ),
            ),
        )
        with self.assertRaises(OntologyViolation):
            ConnectAgent(SALMON_ONTOLOGY).connect(invalid)

    def test_review_asks_without_explicit_authority(self) -> None:
        result = ReviewAgent().review(reason_result(), HumanEvidence())
        self.assertEqual(GateDecision.ASK, result.decision)

    def test_review_rejects_hypothesis_reason_did_not_offer(self) -> None:
        result = ReviewAgent().review(
            reason_result(),
            HumanEvidence(
                selected_hypothesis="pizza",
                accepts_retained_unknowns=True,
                authorizes_bounded_guidance=True,
            ),
        )
        self.assertEqual(GateDecision.ASK, result.decision)
        self.assertIn("fish", result.reasons[0])

    def test_review_keeps_unknown_hypothesis_outside_action_envelope(self) -> None:
        value = reason_result()
        with_unknown = ReasonResult(
            query=value.query,
            hypotheses=(
                *value.hypotheses,
                Hypothesis(
                    "unresolved_food",
                    "unresolved food",
                    HypothesisStatus.UNKNOWN,
                    ("human conjecture only",),
                ),
            ),
            retained_unknowns=value.retained_unknowns,
            proposed_action=value.proposed_action,
            knowledge=value.knowledge,
        )

        result = ReviewAgent().review(
            with_unknown,
            HumanEvidence(
                selected_hypothesis="unresolved_food",
                accepts_retained_unknowns=True,
                authorizes_bounded_guidance=True,
            ),
        )

        self.assertEqual(GateDecision.ASK, result.decision)
        self.assertIn("unknown hypothesis", result.reasons[0])

    def test_reason_rejects_empty_retrieval(self) -> None:
        value = perception()
        connected = ConnectAgent(SALMON_ONTOLOGY).connect(value)
        with self.assertRaisesRegex(ValueError, "no chunks"):
            asyncio.run(ReasonAgent(EmptyKnowledge()).reason(value, connected))

    def test_act_rejects_review_bypass(self) -> None:
        review = ReviewResult(GateDecision.ASK, ("missing",), ("identity",))
        with self.assertRaises(PermissionError):
            ActAgent().act(reason_result(), review)

    def test_act_rejects_uncited_temperature_claim(self) -> None:
        value = reason_result()
        unsupported = ReasonResult(
            query=value.query,
            hypotheses=value.hypotheses,
            retained_unknowns=value.retained_unknowns,
            proposed_action=value.proposed_action,
            knowledge=KnowledgeResult(
                query=value.knowledge.query,
                model=value.knowledge.model,
                chunks=(),
                mcp_call=value.knowledge.mcp_call,
            ),
        )
        review = ReviewResult(
            GateDecision.ALLOW_BOUNDED,
            ("authorized",),
            ("identity",),
            selected_hypothesis="fish",
        )
        with self.assertRaisesRegex(ValueError, "145"):
            ActAgent().act(unsupported, review)

    def test_act_renders_the_reviewed_hypothesis(self) -> None:
        value = reason_result()
        with_salmon = ReasonResult(
            query=value.query,
            hypotheses=(
                *value.hypotheses,
                Hypothesis(
                    "salmon",
                    "salmon",
                    HypothesisStatus.PLAUSIBLE,
                    ("model assertion limited by missing label",),
                ),
            ),
            retained_unknowns=value.retained_unknowns,
            proposed_action=value.proposed_action,
            knowledge=value.knowledge,
        )
        review = ReviewResult(
            GateDecision.ALLOW_BOUNDED,
            ("authorized",),
            ("identity",),
            selected_hypothesis="salmon",
        )

        action = ActAgent().act(with_salmon, review)

        self.assertIn("human-selected salmon hypothesis", action.guidance)

    def test_act_rejects_unreviewed_hypothesis(self) -> None:
        review = ReviewResult(
            GateDecision.ALLOW_BOUNDED,
            ("authorized",),
            ("identity",),
            selected_hypothesis="pizza",
        )
        with self.assertRaisesRegex(PermissionError, "reviewed"):
            ActAgent().act(reason_result(), review)

    def test_learn_rejects_outcome_without_cited_action(self) -> None:
        uncited = ActionResult(
            guidance="unsupported",
            authority="test",
            citation_chunk_ids=(),
        )
        with self.assertRaisesRegex(ValueError, "cited action"):
            LearnAgent().learn(uncited, outcome="result", feedback=None)

    def test_guard_rejects_transition_without_required_artifact(self) -> None:
        with self.assertRaises(PermissionError):
            GuardPolicy().require_transition(Stage.REASON, has_connected_event=False)


if __name__ == "__main__":
    unittest.main()
