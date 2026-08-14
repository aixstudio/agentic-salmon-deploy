from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from agentic_salmon.cli import _display_interrupt, _prompt_review


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
        with patch("builtins.input", side_effect=["9"]) as prompt:
            evidence = _prompt_review(self.payload)

        self.assertEqual("9", evidence.selected_hypothesis)
        self.assertIsNone(evidence.accepts_retained_unknowns)
        self.assertIsNone(evidence.authorizes_bounded_guidance)
        prompt.assert_called_once()

    def test_unknown_selection_returns_to_review_without_authorization(self) -> None:
        with patch("builtins.input", side_effect=["1"]) as prompt:
            evidence = _prompt_review(self.payload)

        self.assertEqual("unresolved_food", evidence.selected_hypothesis)
        self.assertIsNone(evidence.authorizes_bounded_guidance)
        prompt.assert_called_once()

    def test_valid_selection_collects_explicit_human_evidence(self) -> None:
        displayed = io.StringIO()
        with redirect_stdout(displayed):
            _display_interrupt(self.payload, "test-run")

        responses = ["2", "y", "yes", "home freezer", "seasoning odor"]
        with patch("builtins.input", side_effect=responses) as prompt:
            evidence = _prompt_review(self.payload)

        self.assertEqual("fish", evidence.selected_hypothesis)
        self.assertTrue(evidence.accepts_retained_unknowns)
        self.assertTrue(evidence.authorizes_bounded_guidance)
        self.assertEqual("home freezer", evidence.storage_recollection)
        self.assertEqual("seasoning odor", evidence.odor_observation)
        self.assertEqual(5, prompt.call_count)
        self.assertIn("1) unresolved food", displayed.getvalue())
        self.assertIn("2) fish", displayed.getvalue())
        self.assertIn("(key: fish)", displayed.getvalue())


if __name__ == "__main__":
    unittest.main()
