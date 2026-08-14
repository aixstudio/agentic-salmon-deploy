# ADR 0001 — Controlled Workflow Before Autonomous Planning

## Status

Accepted for the public baseline.

## Context

The demonstration needs to show agentic behavior without implying that model confidence can establish food identity, freshness, or safety. A free-form planner could make the story look more autonomous, but it would blur the evidence and authority boundaries that the project exists to explain.

## Decision

Use an explicit six-stage workflow—perceive, connect, reason, review, act, and learn—with Guard enforcing transitions and authority.

- Perception records ID-bound observable claims, source, unknowns, unresolved entity mentions, and separately sourced candidate hypotheses. It emits no uncalibrated confidence number.
- Connect resolves candidate mentions, validates relationships against the governed ontology, and assembles one evidence-backed event.
- Reason forms a case-aware query, calls a semantic RAG capability through MCP, and emits source-bound hypotheses without publishing hidden reasoning.
- Review is a resumable LangGraph interrupt and returns `ASK`, `STOP`, or `ALLOW_BOUNDED` from explicit human evidence. An invalid hypothesis, or one still classified as unknown, remains interrupted and cannot reach Act.
- Action is unavailable unless Guard sees `ALLOW_BOUNDED`; it must render the actual reviewed hypothesis, and temperature guidance requires a supporting retrieved citation.
- Learning records preference feedback but cannot modify safety policy.

The public baseline uses reviewed observations cryptographically bound to the sanitized real input image, so it runs without credentials and makes no fabricated claim that the baseline performs vision inference. Its knowledge capability uses a reviewed local corpus, FastEmbed dense embeddings, in-memory cosine ranking, and the official MCP Python SDK over stdio. No vector database or hosted retrieval service is required.

## Consequences

- Behavior is explainable, testable, and easy to demonstrate.
- Entity resolution and event assembly have their own contract, failures, trace, and tests instead of being hidden inside reasoning.
- Human authority is enforced in code instead of described only in prose.
- Retrieval is visibly replaceable through a typed port without changing Reason or the LangGraph topology.
- The first real run downloads the configured embedding model; deterministic unit tests remain network-free.
- Adding a real vision provider later requires evaluation and threat-model updates, not a workflow rewrite.
