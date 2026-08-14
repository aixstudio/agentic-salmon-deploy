"""Act agent: render only the intervention authorized by Review and Guard."""

from __future__ import annotations

from .models import (
    ActionResult,
    GateDecision,
    HypothesisStatus,
    ReasonResult,
    ReviewResult,
)


class ActAgent:
    def act(self, reason: ReasonResult, review: ReviewResult) -> ActionResult:
        if review.decision is not GateDecision.ALLOW_BOUNDED:
            raise PermissionError("Act requires ALLOW_BOUNDED")
        selected = next(
            (
                item
                for item in reason.hypotheses
                if item.hypothesis_id == review.selected_hypothesis
            ),
            None,
        )
        if selected is None or selected.status is HypothesisStatus.UNKNOWN:
            raise PermissionError(
                "Act requires the reviewed supported or plausible hypothesis"
            )
        citations = tuple(
            chunk.chunk_id
            for chunk in reason.knowledge.chunks
            if "145" in chunk.text and "thermometer" in chunk.text.lower()
        )
        if not citations:
            raise ValueError("Act requires a retrieved citation for its 145°F guidance")
        return ActionResult(
            guidance=(
                "Identity remains unverified. If you proceed under your human-selected "
                f"{selected.name} hypothesis, do not rely on appliance time or "
                "appearance alone; "
                "measure the center with a food thermometer and use the cited 145°F "
                "fish guidance. Stop if you have a storage, odor, allergy, or identity concern."
            ),
            authority="human-authorized bounded guidance",
            citation_chunk_ids=citations,
        )
