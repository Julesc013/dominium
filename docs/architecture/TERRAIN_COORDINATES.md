Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Terrain Coordinates (TERRAIN0)

Status: binding.
Scope: coordinate frames and precision for terrain domains.

## Frames
Terrain coordinates are hierarchical:
1) Domain frame (global)
2) Body frame (local reference for a domain volume)
3) Chunk frame (bounded, LOD-aware)
4) Cell frame (micro detail)

## Deterministic mapping
- Lat/long or spherical mappings are deterministic and data-defined.
- All mappings are replayable and versioned.
- Coordinate transforms use no floating point in authoritative code.

## Precision policy
- Authoritative transforms use fixed-point or rational representations.
- Quantization scales are explicit and per-frame.
- Presentation layers may use floating point for display only.

## See also
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/UNIT_SYSTEM_POLICY.md`