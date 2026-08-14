from __future__ import annotations

import unittest
from unittest.mock import patch

from agentic_salmon.cli import _prompt_review


class CliReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "offered_hypotheses": [
                {
                    "hypothesis_id": "unresolved_food",
                    "label": "unresolved food",
                    "status": "unknown",
                    "action_eligible": False,
                },
                {
                    "hypothesis_id": "fish",
                    "label": "fish",
                    "status": "supported",
                    "action_eligible": True,
                },
            ]
        }

    def test_invalid_selection_returns_to_review_without_extra_prompts(self) -> None:
        with patch("builtins.input", side_effect=["pizza"]) as prompt:
            evidence = _prompt_review(self.payload)

        self.assertEqual("pizza", evidence.selected_hypothesis)
        self.assertIsNone(evidence.accepts_retained_unknowns)
        self.assertIsNone(evidence.authorizes_bounded_guidance)
        prompt.assert_called_once()

    def test_unknown_selection_returns_to_review_without_authorization(self) -> None:
        with patch("builtins.input", side_effect=["unresolved_food"]) as prompt:
            evidence = _prompt_review(self.payload)

        self.assertEqual("unresolved_food", evidence.selected_hypothesis)
        self.assertIsNone(evidence.authorizes_bounded_guidance)
        prompt.assert_called_once()

    def test_valid_selection_collects_explicit_human_evidence(self) -> None:
        responses = ["fish", "y", "yes", "home freezer", "seasoning odor"]
        with patch("builtins.input", side_effect=responses) as prompt:
            evidence = _prompt_review(self.payload)

        self.assertEqual("fish", evidence.selected_hypothesis)
        self.assertTrue(evidence.accepts_retained_unknowns)
        self.assertTrue(evidence.authorizes_bounded_guidance)
        self.assertEqual("home freezer", evidence.storage_recollection)
        self.assertEqual("seasoning odor", evidence.odor_observation)
        self.assertEqual(5, prompt.call_count)


if __name__ == "__main__":
    unittest.main()
