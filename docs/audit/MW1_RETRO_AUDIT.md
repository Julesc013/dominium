Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MW1 Retro Audit

## Scope

This audit records the repository state before MW-1 star-system seed artifact and discovery work.

Audit targets:

- GEO-8 refinement flow
- `kind.star_system` identity and object-kind readiness
- existing teleport and navigation-query surfaces

## Existing GEO-8 Refinement Flow

Current worldgen already supports the MW-1 transition from seed discovery to star-system instantiation.

Relevant surfaces:

- `schema/geo/worldgen_request.schema`
  - explicit `refinement_level`
  - explicit `reason`
- `src/geo/worldgen/worldgen_engine.py`
  - `L0` already returns deterministic per-cell seed descriptors
  - `L1` already emits `kind.star_system` object IDs from MW-0 local indices
  - process cache keys are derived from immutable universe lineage plus cell/refinement inputs
- `tools/xstack/sessionx/process_runtime.py`
  - `process.worldgen_request` is the authoritative mutation boundary
  - repeated worldgen requests are merged by `result_id` and `cache_key`
  - spawned objects are de-duplicated by `object_id_hash`

Audit conclusion:

- MW-1 can extend refinement `L1` without reopening the GEO request/result contract.
- Idempotent star-system artifact persistence should be attached to the existing `process.worldgen_request` flow, not added as a new mutation path.

## Existing Object Kind Readiness

`data/registries/object_kind_registry.json` already declares:

- `kind.star_system`

Current identity law:

- `src/geo/index/object_id_engine.py`
  - stable IDs derived from `universe_identity_hash + geo_cell_key + object_kind_id + local_subkey`

Current MW-0 local subkey rule:

- `src/worldgen/mw/mw_cell_generator.py`
  - `local_subkey = star_system:<local_index>`

Audit conclusion:

- MW-1 does not need a new object-kind declaration.
- `kind.star_system` identity is already compatible with the MW-0 constitution and overlay-safe lineage rules.

## Existing Teleport And Query Surfaces

Existing teleport surface:

- `tools/xstack/sessionx/process_runtime.py`
  - `process.camera_teleport`
  - resolves `target_object_id` through `navigation_indices["astronomy_catalog_index"]`
  - resolves deterministic base position from astronomy/ephemeris payloads

Existing navigation/query surfaces:

- `tools/xstack/registry_compile/compiler.py`
  - builds static `astronomy.catalog.index.json` from pack content
- `tools/xstack/sessionx/process_runtime.py`
  - `_navigation_maps(...)`
  - `_astronomy_entries(...)`
- `tools/mvp/runtime_entry.py`
  - CLI already accepts `--teleport`

Limitations before MW-1:

- static astronomy index is pack/catalog driven, not procedural MW-cell driven
- no procedural nearest-system query surface exists
- no habitable-likely filtering surface exists
- no replay tool exists for deterministic system-artifact instantiation

Audit conclusion:

- MW-1 should add a procedural query/index layer for star systems rather than mutating the static registry compiler into a runtime worldgen surface.
- Teleport integration can reuse the existing `target_object_id` path if MW-1 exposes deterministic star-system entries in astronomy-index shape.

## Existing Reusable Fixtures And Replay Surfaces

Reusable verification surfaces already present:

- `tools/xstack/testx/tests/geo8_testlib.py`
  - deterministic worldgen process fixture
- `tools/geo/tool_replay_worldgen_cell.py`
  - replay/hash verification pattern for repeated worldgen
- `tools/xstack/sessionx/process_runtime.py`
  - worldgen request/result artifact persistence

Audit conclusion:

- MW-1 can reuse the GEO-8 fixture pattern and replay-tool pattern without inventing a parallel verification stack.
