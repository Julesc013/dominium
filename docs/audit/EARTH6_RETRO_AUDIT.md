Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EARTH-6 Retro Audit

## Audit Targets

- current `process.body_tick` and `process.body_apply_input` mutation paths
- body-state synchronization and direct-position-write risk
- available surface elevation proxy access through surface tiles and GEO-7 geometry state
- deterministic geometry-edit refresh hooks for local terrain changes

## Findings

### Body integration already stays inside deterministic processes

- `tools/xstack/sessionx/process_runtime.py` owns:
  - `process.body_apply_input`
  - `process.body_tick`
- `process.body_apply_input` already converts intent into PHYS force applications.
- `process.body_tick` already integrates momentum, applies damping, resolves body-body collisions, and then syncs body state.
- Conclusion:
  - EARTH-6 can extend the same process path with terrain contact and slope response without adding any UI or renderer mutation path.

### Position writes are concentrated and reviewable

- The only authoritative body transform writes found for embodiment are inside `process_runtime.py`.
- `src/embodiment/body/body_system.py` only seeds template rows and canonical initial state.
- `src/client/*` view code reads snapshots and derived artifacts only.
- Conclusion:
  - The direct-position-write risk surface remains bounded to process runtime and existing RepoX/AuditX hooks can be extended instead of introducing new mutation surfaces.

### Deterministic terrain height inputs already exist

- `worldgen_surface_tile_artifacts` already expose:
  - `tile_cell_key`
  - `elevation_params_ref.height_proxy`
  - hydrology-adjusted height through `extensions.hydrology_effective_height_proxy`
- GEO-7 geometry rows already expose per-cell `height_proxy` overrides.
- Existing EARTH-1 and EARTH-2 helpers already use the precedence:
  1. geometry override
  2. hydrology-adjusted height
  3. base surface elevation proxy
- Conclusion:
  - EARTH-6 can reuse this precedence directly for macro collision height queries.

### GEO neighbor ordering is already deterministic

- `src.geo.index.geo_index_engine.geo_cell_key_neighbors(...)` resolves neighbors through canonical GEO ordering and stable alias reconstruction.
- `tools/xstack/sessionx/process_runtime.py::_runtime_neighbor_window(...)` already uses the same deterministic neighborhood surface for local hydrology recompute.
- Conclusion:
  - EARTH-6 slope estimation and local dirty-region refresh can rely on existing GEO neighbor order without inventing a new topology path.

### Geometry edits already expose a bounded local recompute pattern

- `process.geometry_*` currently calls `_recompute_surface_tile_hydrology(...)` using dirty tile keys and local neighbor expansion.
- The refresh is local and deterministic, not a global surface rebuild.
- Conclusion:
  - EARTH-6 can use the same dirty-tile boundary to invalidate cached collision samples and keep geometry edits collision-safe without requiring global terrain recompute.

## Compatibility Check

- No mesh assets are required for EARTH-6.
- No rigid-body solver or continuous collision path is required for the MVP ground-contact goal.
- The missing pieces are:
  - a declared collision-provider contract
  - slope-response parameters
  - a deterministic macro heightfield provider
  - process-only ground contact and debug surfaces
