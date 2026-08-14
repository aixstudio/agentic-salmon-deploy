"""Perceive agent: capture sourced observations without upgrading hypotheses."""

from __future__ import annotations

from .models import Perception
from .providers import VisionProvider


class PerceiveAgent:
    def __init__(self, provider: VisionProvider) -> None:
        self.provider = provider

    def perceive(self) -> Perception:
        perception = self.provider.perceive()
        if not perception.provenance.strip():
            raise ValueError("Perceive requires explicit provenance")
        if not perception.observations:
            raise ValueError("Perceive requires at least one reviewed observation")
        if not perception.unknowns:
            raise ValueError("Perceive must preserve evidence unknowns")
        observation_ids = [item.observation_id for item in perception.observations]
        if any(not item.strip() for item in observation_ids):
            raise ValueError("Perceive requires stable observation IDs")
        if len(observation_ids) != len(set(observation_ids)):
            raise ValueError("Perceive observation IDs must be unique")
        candidate_ids = [
            item.hypothesis_id for item in perception.candidate_hypotheses
        ]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("Perceive candidate hypothesis IDs must be unique")
        known_observations = set(observation_ids)
        for candidate in perception.candidate_hypotheses:
            unknown_support = (
                set(candidate.supporting_observation_ids) - known_observations
            )
            if unknown_support:
                raise ValueError(
                    "candidate hypothesis references unknown observations: "
                    f"{sorted(unknown_support)}"
                )
        return perception
