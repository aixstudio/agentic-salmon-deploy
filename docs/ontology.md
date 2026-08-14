# Connect and the Agentic Salmon Ontology

Connect is a first-class workflow capability because deciding what belongs together is different from deciding what it means.

```mermaid
flowchart LR
    P[Perceive<br/>observable claims + mentions] --> C[Connect<br/>resolve + assemble]
    O[Governed ontology<br/>entity kinds + relation rules] -. constrains .-> C
    C --> G[Connected event<br/>case instance graph]
    G --> R[Reason<br/>evaluate + identify missing evidence]
```

## Governed Meaning

The small ontology permits only these entity kinds and relationships:

| Subject | Relationship | Object |
| --- | --- | --- |
| `food_portion` | `located_in` | `cooking_equipment` |
| `food_portion` | `has_visible_feature` | `observable_feature` |

The ontology is the reusable semantic contract. It says which relationship shapes are meaningful; it does not claim that a relationship occurred.

## Case Instance Graph

The reviewed fixture supplies unresolved, evidence-bound mentions from the real input image. Connect applies the event-scoped resolution policy, maps those mentions to canonical IDs, validates the ontology, and emits this case-specific graph:

```mermaid
flowchart LR
    F[food_portions_1<br/>food_portion]
    B[cooking_equipment_1<br/>cooking_equipment]
    S[observable_feature_1<br/>observable_feature]
    F -->|located_in| B
    F -->|has_visible_feature| S
```

Every emitted entity and relationship retains an evidence claim. An unknown mention, conflicting entity kind, missing endpoint, or disallowed relationship fails the Connect stage instead of leaking ambiguity into Reason.

## Ownership Boundary

- Perceive answers: what observations, sourced candidate hypotheses, unknowns, and unresolved mentions arrived?
- Connect answers: which entities and relationships form this event?
- Reason answers: what does the connected event mean, and what evidence is still missing?

That separation keeps entity resolution visible, testable, and reusable without turning the demonstration into a general knowledge graph platform.
