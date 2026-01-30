# Terrain Geometry Baseline (TERRAIN1)

Status: baseline.
Scope: minimal terrain surface realization for T1.

## What exists
- Terrain truth is the SDF field `terrain.phi` (see `docs/architecture/TERRAIN_TRUTH_MODEL.md`).
- A procedural base provider resolves:
  - `terrain.phi`
  - `terrain.material_primary`
  - `terrain.roughness`
  - `travel.cost`
- Shapes supported: sphere, oblate spheroid, superflat slab.
- Surface variation is seeded noise only; no erosion or strata yet.
- Collision and walkability derive from `terrain.phi`, gradient, and slope.
- Mesh extraction uses deterministic marching cubes and is view-only.
- Coordinates are fixed-point with local chunk and player-local frames.

## What does not exist yet
- No mining, erosion, decay, or regeneration systems.
- No per-tick global simulation or background mutation.
- No overlays beyond Process-only edit contracts (T2+).
- No planet/station special casing or hard-coded body types.

## Determinism and scaling
- All authoritative transforms and sampling are fixed-point.
- Sampling cost is bounded by the domain policy budget ladder.
- Tiles and caches are disposable; the provider chain is canonical.

## Why these omissions
T1 is a surface realization only. Higher layers (subsurface geology, resources,
construction, destruction) are deferred to later prompts so that the terrain
truth model and determinism guarantees are locked first.

## See also
- `docs/worldgen/TERRAIN_STORAGE_STRATEGY.md`
- `docs/architecture/TERRAIN_FIELDS.md`
- `docs/architecture/TERRAIN_COORDINATES.md`
