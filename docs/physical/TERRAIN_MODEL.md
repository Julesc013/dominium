Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# TERRAIN MODEL

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






Terrain MUST be represented as layered fields over domains with explicit units and LOD bounds.


Fields MUST be typed, deterministic, and allow latent/unknown/inferred values.


Geometry MUST be derived; geometry MUST NOT be authoritative.


Terrain mutation MUST occur only via processes that declare affected fields and constraints.





Terrain systems MUST NOT assume human-centric or Earth-centric defaults.


Terrain systems MUST NOT rely on "AI magic" or hidden heuristics.





References:


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
