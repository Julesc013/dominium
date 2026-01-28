# TERRAIN MODEL

Terrain MUST be represented as layered fields over domains with explicit units and LOD bounds.
Fields MUST be typed, deterministic, and allow latent/unknown/inferred values.
Geometry MUST be derived; geometry MUST NOT be authoritative.
Terrain mutation MUST occur only via processes that declare affected fields and constraints.

Terrain systems MUST NOT assume human-centric or Earth-centric defaults.
Terrain systems MUST NOT rely on "AI magic" or hidden heuristics.

References:
- docs/architecture/INVARIANTS.md
- docs/architecture/REALITY_LAYER.md
