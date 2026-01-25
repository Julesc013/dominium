# TOOLING OVERVIEW

Tooling MUST be read-only and MUST NOT alter simulation state.
Tooling MUST operate on snapshots, event streams, and history artifacts only.
Tooling MUST respect epistemic limits; privileged access MUST be explicit.
Tooling MUST be deterministic and headless-safe.

Supported tool classes (non-exhaustive):
- World inspector (fields, topology, unknown/latent)
- Agent inspector (goals, beliefs, memory, plans, failures)
- Institution inspector (constraints, enforcement, collapse)
- History and replay viewer (timelines, provenance, diffs)
- Pack and capability inspector (precedence, overrides, missing capabilities)
- Determinism/regression tools (divergence points, hashes)

References:
- docs/arch/INVARIANTS.md
- docs/arch/REALITY_LAYER.md
