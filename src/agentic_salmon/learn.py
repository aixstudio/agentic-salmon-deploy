"""Learn agent: retain outcome evidence without weakening policy."""

from __future__ import annotations

from .models import ActionResult, LearnResult


class LearnAgent:
    def learn(
        self,
        action: ActionResult,
        *,
        outcome: str | None,
        feedback: str | None,
    ) -> LearnResult:
        if not action.citation_chunk_ids:
            raise ValueError("Learn requires the cited action that preceded the outcome")
        return LearnResult(
            outcome=outcome,
            preference_feedback=feedback,
            policy_effect="none; outcome evidence cannot weaken safety or authority policy",
        )
