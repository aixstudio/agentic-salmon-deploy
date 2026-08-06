from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from agentic_salmon.providers import ReviewedFixtureProvider


class ProviderTests(unittest.TestCase):
    def test_reviewed_fixture_is_bound_to_input_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "input.jpeg"
            image.write_bytes(b"reviewed image")
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            fixture = root / "fixture.json"
            fixture.write_text(
                json.dumps(
                    {
                        "provenance": "test",
                        "input_image_sha256": digest,
                        "observations": [],
                        "unknowns": [],
                    }
                ),
                encoding="utf-8",
            )

            perception = ReviewedFixtureProvider(fixture, image).perceive()

        self.assertEqual(digest, perception.input_image_sha256)

    def test_changed_image_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "input.jpeg"
            image.write_bytes(b"changed image")
            fixture = root / "fixture.json"
            fixture.write_text(
                json.dumps(
                    {
                        "provenance": "test",
                        "input_image_sha256": "0" * 64,
                        "observations": [],
                        "unknowns": [],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "does not match"):
                ReviewedFixtureProvider(fixture, image).perceive()


if __name__ == "__main__":
    unittest.main()
