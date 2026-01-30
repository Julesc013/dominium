# Geology Storage Strategy (GEOLOGY2)

Status: baseline.
Scope: sparse storage and collapse/expand for subsurface geology and resources.

## Choice: hashed domain tiles (shared with terrain)
Geology uses the same hashed domain tile strategy as terrain:

- Tiles are addressed by deterministic hashes of (tx, ty, tz, resolution).
- Each tile stores strata ids, hardness/fracture fields, and resource density samples.
- The cache is disposable and may be cleared at any time.
- Authoritative truth remains provider-derived fields, not cached tiles.

## LOD ladder
Resolution selection is deterministic and budgeted:

1) Full (direct eval)
2) Medium (tile samples)
3) Coarse (tile samples)
4) Analytic (provider eval)

The ladder is policy-driven per `docs/architecture/SCALING_MODEL.md`.

## Collapse/expand (macro capsules)
Collapsed tiles are removed from cache and summarized into macro capsules.
Capsules store:
- Invariants (coarse): total resource mass per domain tile, strata proportions.
- Sufficient statistics: resource density histograms, hardness distribution.
- Provenance and extension bag.

Expand regenerates tiles deterministically from providers. No RNG cursor is
required yet because geology noise is hash-based and time-invariant.

## Rationale
- Sparse, infinite-L0D storage without global voxel grids.
- Constant-cost sampling bounded by domain policy budgets.
- Deterministic collapse/expand compatible with replay and audit.

## See also
- `docs/worldgen/TERRAIN_STORAGE_STRATEGY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/TERRAIN_PROVIDER_CHAIN.md`
