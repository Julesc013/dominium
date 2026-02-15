Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0-draft
Compatibility: Bound to canon v1.0.0 and aligned with `docs/architecture/TERRAIN_COORDINATES.md`.

# Coordinate Model (Draft Contract)

## Purpose
Define deterministic coordinate frames and transform contracts for galaxy navigation and local refinement.

## Coordinate Frames
1. Domain frame (global).
2. Body frame (domain-local reference).
3. Chunk frame (bounded region).
4. Cell frame (micro detail).

## Intended Transform Contract Fields
- `from_frame`
- `to_frame`
- `transform_id`
- `quantization_policy_id`
- `fixed_point_scale`
- `version_ref`
- `extensions{}`

## Invariants
- Authoritative transforms use fixed-point/rational arithmetic only.
- Transform definitions are versioned and replayable.
- Floating-point values are presentation-only.
- Cross-frame mapping is deterministic and independent of thread scheduling.

## Example
```yaml
transform:
  from_frame: domain
  to_frame: chunk
  transform_id: transform.domain_to_chunk.v1
  quantization_policy_id: quant.default.mm
  fixed_point_scale: q16_16
  version_ref: coord.v1.0.0
```

## TODO
- Add canonical rounding and overflow semantics for each fixed-point profile.
- Add deterministic tie-break rules for boundary-inclusive coordinate tests.
- Add reference fixtures for cross-platform transform equivalence.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/architecture/time_model.md`
- `docs/architecture/truth_model.md`
