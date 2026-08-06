from __future__ import annotations

import json
import unittest

from agentic_salmon.models import GateDecision, HumanEvidence, Observation, Perception
from agentic_salmon.workflow import AgenticSalmonWorkflow


class StaticProvider:
    def perceive(self) -> Perception:
        return Perception(
            observations=(
                Observation(
                    claim="Two wrapped fish portions are visible.",
                    confidence=0.95,
                    source="test fixture",
                ),
            ),
            unknowns=("food identity", "storage history", "odor"),
            provenance="test fixture",
        )


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = AgenticSalmonWorkflow(StaticProvider())

    def test_missing_human_evidence_asks_and_does_not_act(self) -> None:
        result = self.workflow.run(HumanEvidence())

        self.assertEqual(GateDecision.ASK, result.decision)
        self.assertIsNone(result.guidance)
        self.assertEqual(["perceive", "reason", "review"], [e.stage.value for e in result.events])

    def test_failed_human_check_stops(self) -> None:
        result = self.workflow.run(
            HumanEvidence(label_identified=True, remained_frozen=False, odor_normal=True)
        )

        self.assertEqual(GateDecision.STOP, result.decision)
        self.assertIsNone(result.guidance)

    def test_confirmed_evidence_allows_action_and_records_feedback(self) -> None:
        result = self.workflow.run(
            HumanEvidence(label_identified=True, remained_frozen=True, odor_normal=True),
            feedback="wonderful",
        )

        self.assertEqual(GateDecision.ALLOW, result.decision)
        self.assertIsNotNone(result.guidance)
        self.assertEqual("learn", result.events[-1].stage.value)
        self.assertEqual("wonderful", result.events[-1].evidence["preference_feedback"])

    def test_public_trace_excludes_private_reasoning_and_prompts(self) -> None:
        result = self.workflow.run(HumanEvidence())
        serialized = json.dumps(result.to_dict()).lower()

        self.assertNotIn("chain-of-thought", serialized)
        self.assertNotIn("hidden_reasoning", serialized)
        self.assertNotIn("system_prompt", serialized)


if __name__ == "__main__":
    unittest.main()
