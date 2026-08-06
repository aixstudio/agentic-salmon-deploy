"""Perception providers.

The baseline provider reads a reviewed fixture. A model-backed adapter can be
added later without changing workflow policy.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

from .models import Observation, Perception


class VisionProvider(Protocol):
    def perceive(self) -> Perception:
        """Return observable claims, explicit unknowns, and provenance."""


class ReviewedFixtureProvider:
    def __init__(self, fixture_path: Path, input_image: Path) -> None:
        self.fixture_path = fixture_path
        self.input_image = input_image

    def perceive(self) -> Perception:
        data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        actual_sha256 = _sha256(self.input_image)
        expected_sha256 = data["input_image_sha256"]
        if actual_sha256 != expected_sha256:
            raise ValueError(
                "input image does not match the reviewed fixture: "
                f"expected {expected_sha256}, got {actual_sha256}"
            )
        observations = tuple(
            Observation(
                claim=item["claim"],
                confidence=float(item["confidence"]),
                source=item["source"],
            )
            for item in data["observations"]
        )
        return Perception(
            observations=observations,
            unknowns=tuple(data["unknowns"]),
            provenance=data["provenance"],
            input_image_sha256=actual_sha256,
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
