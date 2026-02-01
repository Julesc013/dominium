Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Terrain Storage Strategy (TERRAIN1)

Status: baseline.
Scope: sparse storage and LOD strategy for terrain surface realization.

## Choice: hashed SDF chunks (domain tiles)
Terrain uses the existing domain tile system as the sparse storage layer:

- Tiles are addressed by deterministic hashes of (tx, ty, tz, resolution).
- Each tile stores a fixed SDF sample grid at a given resolution.
- The cache is disposable and may be cleared at any time.
- The authoritative truth remains the provider chain defined in
  `docs/architecture/TERRAIN_TRUTH_MODEL.md`.

## LOD ladder
Resolution is selected by policy and budget:

1) Full (direct eval)
2) Medium (tile samples)
3) Coarse (tile samples)
4) Analytic (provider analytic eval)

Resolution selection is deterministic and cost-bounded per
`docs/architecture/DETERMINISTIC_ORDERING_POLICY.md` and
`docs/architecture/SCALING_MODEL.md`.

## Collapse/expand
Collapsed tiles are represented by macro capsules and are removed from the
tile cache. Expand regenerates tiles deterministically from the provider chain.

## Rationale
- Sparse and infinite LOD without global rebuilds.
- Constant-cost sampling bounded by per-query budgets.
- Deterministic hashing and ordering support replay and audit.

## See also
- `docs/architecture/TERRAIN_PROVIDER_CHAIN.md`
- `docs/architecture/TERRAIN_MACRO_CAPSULE.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`