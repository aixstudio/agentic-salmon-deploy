# Agentic Salmon

**Owner:** Joseph Shi — [aixstudio](https://github.com/aixstudio) — Principal Architect - Agentic AI & Data Platform | I build with Python

> The agent refused to hallucinate dinner. That is when the architecture started working.

Agentic Salmon is a small, locally runnable demonstration of controlled agentic
AI—not a cooking application:

```text
GUARD ⊣ [PERCEIVE → CONNECT → REASON → REVIEW → ACT → LEARN]
```

Each name is an executable cognitive ownership boundary. Guard is not a seventh
agent; it controls which transitions and actions are permitted. LangGraph
schedules and checkpoints the six contracts and pauses at a real human Review
interrupt.

![Two seasoned food portions arranged in an air-fryer basket before cooking](docs/assets/salmon-pre-cook-input.jpeg)

## What the Demo Proves

- Perceive separates sourced observations, hypotheses, and unknowns.
- Connect resolves entities and assembles an event constrained by an ontology.
- Reason invokes semantic RAG through a real MCP client/server tool call.
- Review returns `ASK`, `STOP`, or `ALLOW_BOUNDED` from explicit human input.
- Review keeps `unknown` hypotheses outside the action-eligible envelope.
- Act renders the selected supported/plausible hypothesis and releases only cited
  guidance inside the approved authority envelope.
- Learn records the historical outcome without weakening policy.

The RAG plug-in is intentionally small: a reviewed JSON corpus, FastEmbed dense
embeddings, and in-memory cosine ranking. It proves that semantic retrieval can
be plugged into the agent contract through MCP without requiring pgvector, a
hosted service, or credentials.

## Evidence Boundary

No original packaging or label was available. The photograph supports visible
observations such as two portions, seasoning, skin, and the air-fryer basket. It
cannot establish species, ingredients, allergens, smell, storage history,
freshness, or safety. The human may select `fish` as the evidence-supported
working hypothesis while Reason keeps `salmon` separate and merely plausible.
Neither is treated as verified identity.

## Run Locally

Python 3.12 or later is required. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m agentic_salmon demo
```

The first run downloads the configured `BAAI/bge-small-en-v1.5` embedding model.
It then calls the local MCP server, performs semantic retrieval, and stops at
Review with `ASK`. The output includes a run ID, UTC timestamps, measured node
and MCP durations, retrieval scores and citations, retained unknowns, and the
interrupt payload.

For the clearest HITL demonstration, use the interactive runner. It displays
Reason's offered hypotheses, rejects invalid selections without advancing, and
resumes the same run after valid human input:

```bash
.venv/bin/python -m agentic_salmon demo --interactive \
  --outcome "390°F for 14 minutes; wonderful and fresh-tasting" \
  --feedback "moderately spicy result preferred"
```

Run the explicitly authorized historical replay:

```bash
.venv/bin/python -m agentic_salmon demo \
  --review allow-bounded \
  --selected-hypothesis "fish" \
  --storage-recollection "retrieved frozen from home freezer; exact cold chain unknown" \
  --odor-observation "seasoning smelled reminiscent of lasagna" \
  --outcome "390°F for 14 minutes; wonderful and fresh-tasting" \
  --feedback "moderately spicy result preferred"
```

The 390°F/14-minute values are recorded only as historical outcome evidence;
they are not presented as a universal recipe. Act cites reviewed thermometer
guidance and continues to state that identity is unverified.

An ignored Markdown report is also written under `traces/`.

## Test

```bash
LANGGRAPH_STRICT_MSGPACK=true .venv/bin/python -m unittest discover -s tests -v
```

The deterministic tests do not download the embedding model. They cover all six
agent contracts, ontology violations, semantic ranking, a real in-process MCP
tool call, Review interruption/resume, Guard rejection, citation enforcement,
and exclusion of hidden prompt/reasoning fields from public traces.

## Architecture Notes

- [Controlled workflow decision](docs/adr/0001-controlled-workflow.md)
- [Connect and ontology](docs/ontology.md)
- [Threat model](docs/threat-model.md)
- [True story and evidence boundaries](docs/story.md)
- [Image provenance](docs/image-provenance.md)
- [AI assistance disclosure](docs/ai-assistance.md)

## Safety

This is an architecture demonstration, not food-safety, medical, allergy, or
nutritional advice. It does not determine freshness or safety from an image.
USDA guidance says fish should reach **145°F (62.8°C)** as measured with a food
thermometer; appliance time and temperature alone are not proof of doneness.

Source: [USDA Air Fryers and Food Safety](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/air-fryers-and-food-safety).
