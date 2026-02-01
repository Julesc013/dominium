Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# OBSERVATION MODEL





Observers MUST NOT be agents and MUST NOT possess agent_id, authority, or capabilities.


Observers MAY request snapshots, subscribe to event streams, and read history artifacts only.


Objective snapshots MUST require privileged access; subjective snapshots MUST respect epistemic limits.


Snapshot requests MUST declare scope, LOD, and explicit budget; refusals MUST be explicit.


Unknown and latent data MUST be represented explicitly and MUST NOT be silently filled in.


All observation interfaces MUST be read-only and deterministic.





References:


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
