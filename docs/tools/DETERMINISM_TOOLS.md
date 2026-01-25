# DETERMINISM TOOLS

Determinism tools MUST compare runs without mutating state.
Tools MUST detect divergence points and provide deterministic hashes.
State diffing MUST rely on recorded snapshots and events only.
Outputs MUST be deterministic for identical inputs.

References:
- docs/arch/INVARIANTS.md
- docs/arch/REALITY_LAYER.md
