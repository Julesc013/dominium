Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# DETERMINISM TOOLS





Determinism tools MUST compare runs without mutating state.


Tools MUST detect divergence points and provide deterministic hashes.


State diffing MUST rely on recorded snapshots and events only.


Outputs MUST be deterministic for identical inputs.





References:


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
