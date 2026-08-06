# Threat Model

## Protected Assets

- Human safety and authority.
- Personal images and household context.
- Credentials and provider configuration.
- Private prompts, sessions, traces, and research notes.
- Accuracy of the public architectural claim.

## Primary Risks and Controls

| Risk | Control |
| --- | --- |
| Vision overclaims identity, freshness, or safety | Separate observations from unknowns; require human evidence; never let confidence bypass policy. |
| Prompt injection in labels or image-associated text | Treat extracted text as untrusted data; model adapters cannot alter policy or tool authority. |
| Unsafe action after missing evidence | Deterministic `ASK`/`STOP`/`ALLOW` gate with negative-path tests. |
| Preference feedback weakens safety rules | Learning records preference only; policy is code-controlled and unchanged. |
| Personal metadata leaks through media | Keep raw media private; publish only reviewed crops with metadata removed. |
| Chats or hidden reasoning enter Git | Clean-room allowlist export; deny session, prompt, trace, and private paths. |
| Credentials enter source or traces | Ignore `.env` and traces; keep the public baseline credential-free. |
| Model cooking advice conflicts with authoritative guidance | Do not export raw chat recommendations; cite USDA guidance and require a food thermometer. |

## Boundary

This repository demonstrates architecture. It does not determine food freshness or safety and does not replace authoritative food-safety guidance or human judgment. USDA guidance says fish should reach 145°F (62.8°C), measured with a food thermometer.
