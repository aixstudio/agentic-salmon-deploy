"""Controlled perceive -> reason -> review -> act -> learn workflow."""

from __future__ import annotations

from .models import (
    GateDecision,
    HumanEvidence,
    PublicEvent,
    RunResult,
    Stage,
)
from .policies import review
from .providers import VisionProvider


ACTION_GUIDANCE = (
    "Proceed only with the human-selected recipe. USDA guidance says fish should "
    "reach 145°F (62.8°C), measured with a food thermometer; appliance time and "
    "temperature alone do not establish doneness."
)


class AgenticSalmonWorkflow:
    def __init__(self, provider: VisionProvider) -> None:
        self.provider = provider

    def run(
        self,
        evidence: HumanEvidence,
        *,
        feedback: str | None = None,
    ) -> RunResult:
        perception = self.provider.perceive()
        events: list[PublicEvent] = [
            PublicEvent(
                sequence=1,
                stage=Stage.PERCEIVE,
                summary="Recorded observable claims separately from unknowns.",
                evidence={
                    "observations": [
                        {
                            "claim": item.claim,
                            "confidence": item.confidence,
                            "source": item.source,
                        }
                        for item in perception.observations
                    ],
                    "provenance": perception.provenance,
                    "input_image_sha256": perception.input_image_sha256,
                },
            ),
            PublicEvent(
                sequence=2,
                stage=Stage.REASON,
                summary="Identified evidence the visual input cannot establish.",
                evidence={"unknowns": list(perception.unknowns)},
            ),
        ]

        result = review(perception, evidence)
        events.append(
            PublicEvent(
                sequence=3,
                stage=Stage.REVIEW,
                summary=f"Policy gate returned {result.decision.value.upper()}.",
                evidence={
                    "reasons": list(result.reasons),
                    "missing": list(result.missing),
                },
            )
        )

        guidance: str | None = None
        if result.decision is GateDecision.ALLOW:
            guidance = ACTION_GUIDANCE
            events.append(
                PublicEvent(
                    sequence=4,
                    stage=Stage.ACT,
                    summary="Released bounded preparation guidance after human approval.",
                    evidence={"guidance": guidance},
                )
            )

            if feedback is not None:
                learn_evidence: dict[str, str] = {
                    "policy_effect": "none; preference feedback cannot weaken safety policy"
                }
                learn_evidence["preference_feedback"] = feedback
                events.append(
                    PublicEvent(
                        sequence=5,
                        stage=Stage.LEARN,
                        summary="Recorded explicit outcome evidence for preference learning.",
                        evidence=learn_evidence,
                    )
                )

        return RunResult(
            decision=result.decision,
            guidance=guidance,
            events=tuple(events),
        )
