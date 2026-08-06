"""Deterministic review gate for evidence that pixels cannot supply."""

from __future__ import annotations

from .models import GateDecision, HumanEvidence, Perception, ReviewResult


EVIDENCE_LABELS = {
    "label_identified": "human verified the package label and food identity",
    "remained_frozen": "human confirmed appropriate frozen storage history",
    "odor_normal": "human reported no concerning odor after opening",
}


def review(perception: Perception, evidence: HumanEvidence) -> ReviewResult:
    del perception  # The gate depends on missing human evidence, not model confidence.

    values = {
        "label_identified": evidence.label_identified,
        "remained_frozen": evidence.remained_frozen,
        "odor_normal": evidence.odor_normal,
    }
    rejected = tuple(EVIDENCE_LABELS[name] for name, value in values.items() if value is False)
    if rejected:
        return ReviewResult(
            decision=GateDecision.STOP,
            reasons=("A required human safety check failed.", *rejected),
        )

    missing = tuple(EVIDENCE_LABELS[name] for name, value in values.items() if value is None)
    if missing:
        return ReviewResult(
            decision=GateDecision.ASK,
            reasons=("The image cannot supply all evidence required to continue.",),
            missing=missing,
        )

    return ReviewResult(
        decision=GateDecision.ALLOW,
        reasons=("All required human checks were explicitly confirmed.",),
    )
