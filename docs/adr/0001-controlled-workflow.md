# ADR 0001 — Controlled Workflow Before Autonomous Planning

## Status

Accepted for the public baseline.

## Context

The demonstration needs to show agentic behavior without implying that model confidence can establish food identity, freshness, or safety. A free-form planner could make the story look more autonomous, but it would blur the evidence and authority boundaries that the project exists to explain.

## Decision

Use an explicit five-stage workflow—perceive, reason, review, act, and learn—with a deterministic policy gate between review and action.

- Perception records observable claims, confidence, source, and unknowns.
- Reason exposes missing evidence without publishing hidden model reasoning.
- Review returns `ASK`, `STOP`, or `ALLOW` from explicit human evidence.
- Action is unavailable unless the gate returns `ALLOW`.
- Learning records preference feedback but cannot modify safety policy.

Model providers remain behind an interface. The public baseline uses reviewed observations cryptographically bound to the sanitized real input image, so it runs without credentials and makes no fabricated claim that the standard-library baseline performs vision inference.

## Consequences

- Behavior is explainable, testable, and easy to demonstrate.
- Human authority is enforced in code instead of described only in prose.
- The baseline is less flashy than a general autonomous agent.
- Adding a real vision provider later requires evaluation and threat-model updates, not a workflow rewrite.
