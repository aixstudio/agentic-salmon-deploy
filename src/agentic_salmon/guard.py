"""Guard policy controlling transitions without becoming a seventh agent."""

from __future__ import annotations

from .models import GateDecision, ReviewResult, Stage


class GuardPolicy:
    def require_transition(
        self,
        destination: Stage,
        *,
        has_perception: bool = False,
        has_connected_event: bool = False,
        has_reason_result: bool = False,
        review: ReviewResult | None = None,
        has_action: bool = False,
    ) -> None:
        permitted = {
            Stage.CONNECT: has_perception,
            Stage.REASON: has_connected_event,
            Stage.REVIEW: has_reason_result,
            Stage.ACT: review is not None
            and review.decision is GateDecision.ALLOW_BOUNDED,
            Stage.LEARN: has_action,
        }.get(destination, True)
        if not permitted:
            raise PermissionError(f"Guard blocked transition to {destination.value}")
