# Agentic Salmon

> The agent refused to hallucinate dinner. That is when the architecture started working.

Agentic Salmon is a small Python demonstration of a controlled agentic loop:

```text
PERCEIVE -> REASON -> REVIEW -> ACT -> LEARN
```

The loop is not the architecture. The architecture is the control over transitions—what evidence permits the system to advance, what uncertainty triggers a question, and which decisions remain human.

![Two seasoned fish portions arranged in an air-fryer basket before cooking](docs/assets/salmon-pre-cook-input.jpeg)

## The Boundary

A photograph can support observations about visible skin, portions, seasoning, and cooking setup. It cannot establish smell, a discarded package label, storage history, freshness, allergens, or food safety.

This project therefore separates:

- **Observation** — what the supplied evidence supports.
- **Unknowns** — what the evidence cannot establish.
- **Review** — deterministic policy plus explicit human confirmation.
- **Action** — unavailable until the gate returns `ALLOW`.
- **Learning** — preference feedback that cannot weaken safety policy.

## Run Without Credentials

Python 3.12 or later is required. The baseline uses only the standard library.

```bash
PYTHONPATH=src python3 -m agentic_salmon \
  --fixture examples/frozen-salmon-observation.json \
  --input-image docs/assets/salmon-pre-cook-input.jpeg
```

The result is `ASK`, because the visual observations cannot supply the required human evidence.

Run the explicitly approved path:

```bash
PYTHONPATH=src python3 -m agentic_salmon \
  --fixture examples/frozen-salmon-observation.json \
  --input-image docs/assets/salmon-pre-cook-input.jpeg \
  --label-identified yes \
  --remained-frozen yes \
  --odor-normal yes \
  --feedback "best moderately spicy salmon I had cooked"
```

## Test the Decisions

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The tests cover image-fixture integrity, missing evidence, a failed human check, the approved path, and exclusion of private reasoning/prompt fields from the public trace.

## Architecture Notes

- [Controlled workflow decision](docs/adr/0001-controlled-workflow.md)
- [Threat model](docs/threat-model.md)
- [True story and evidence boundaries](docs/story.md)
- [Image provenance](docs/image-provenance.md)
- [AI assistance disclosure](docs/ai-assistance.md)

## Evidence Limitation

The available photograph is the real pre-cook input after the portions were unpacked and arranged in the air-fryer basket. The baseline uses human-reviewed observations bound to that sanitized image's SHA-256. It does not pretend that the standard-library baseline contains a vision model.

A model-backed vision adapter belongs in a later version after its evaluation cases and trust boundary are defined.

## Safety

This is an architecture demonstration, not food-safety, medical, allergy, or nutritional advice. It does not determine freshness or safety from an image. USDA guidance says fish should reach **145°F (62.8°C)** as measured with a food thermometer; appliance time and temperature alone are not proof of doneness.

Source: [USDA Air Fryers and Food Safety](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/air-fryers-and-food-safety).
