Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# VISUALIZATION CONTRACT





Visualization tools MUST consume snapshots and events and MUST NOT mutate simulation state.


Visualization MUST NOT infer hidden truth or bypass epistemic limits.


Visualization MUST tolerate missing, unknown, and latent data and render them explicitly.


Visualization MUST be headless-safe and MUST NOT assume any renderer or UI.


Visualization outputs MUST be deterministic for identical inputs.





References:


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
