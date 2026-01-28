# PLAYER INTENT MODEL

Player input MUST be modeled as intent proposals, goal updates, plan confirmations, or process requests.
Intent MUST NOT mutate state directly.
All intent MUST be validated against authority, epistemics, and physical constraints.
Intent refusal MUST be explicit and recorded.

Intent handling MUST be deterministic and headless-safe.
Intent handling MUST NOT assume UI presence or direct manipulation.

References:
- docs/architecture/INVARIANTS.md
- docs/architecture/REALITY_LAYER.md
