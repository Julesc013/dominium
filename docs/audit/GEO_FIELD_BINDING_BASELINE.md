Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO-4 Field Binding Baseline

## Scope

GEO-4 binds FIELD storage and sampling to canonical `geo_cell_key` identity while preserving the legacy `cell_id` alias for compatibility. Default `R^3` behavior remains unchanged, but FIELD now carries enough topology and partition context to operate on grid, atlas, and future octree-style partitions.

Relevant invariants upheld:
- No mode flags; profile composition only.
- Process-only mutation for authoritative field state.
- Deterministic ordering, cacheability, and replayability.
- Cross-shard field boundary exchange via deterministic boundary artifacts.

## Field Binding Registry Summary

New registry surfaces:
- `data/registries/field_binding_registry.json`
  - binds baseline temperature, moisture, friction, visibility, wind, gravity, irradiance, radiation, and pollution concentration fields to `geo.partition.grid_zd`
  - binds sphere-surface field variants to `geo.partition.atlas_tiles`
- `data/registries/interpolation_policy_registry.json`
  - `interp.nearest`
  - `interp.bilinear_stub`
  - `interp.atlas_nearest`

Canonical schema surfaces:
- `schema/geo/field_binding.schema`
- `schema/geo/interpolation_policy.schema`

## Sampling And Interpolation Policies

Canonical field addressing:
- internal storage normalizes each field cell row by `field_id + geo_cell_key`
- `cell_id` remains a deterministic compatibility alias derived from the GEO key

Sampling APIs:
- `get_field_value(...)`
  - accepts raw spatial position, explicit `geo_cell_key`, or `position_ref + target_frame_id`
- `field_get_value(...)`
  - direct GEO cell lookup
- `field_sample_position_ref(...)`
  - frame-aware sampling path for GEO-2 positions
- `field_sample_neighborhood(...)`
  - neighborhood sampling via `geo_neighbors(...)`

Interpolation:
- nearest-cell is authoritative baseline
- bilinear/atlas policies are deterministic stubs that currently collapse to nearest-cell semantics while preserving the declared policy surface

## Domain Integration Status

Integrated:
- FIELD runtime storage and update loops now canonicalize on `geo_cell_key`
- process runtime records `field_binding_registry_hash` and GEO-aware sample hashes
- compartment/boundary ambient exchange routes through `src/field/field_boundary_exchange.py`
- POLL dispersion continues to route neighborhood iteration through `geo_neighbors(...)`
- THERM ambient field row ordering now respects GEO-bound field rows

Compatibility preserved:
- legacy `cell_id` aliases remain available for existing field, pollution, and save surfaces
- default `geo.topology.r3_infinite` + `geo.partition.grid_zd` semantics remain unchanged

## Proof, Replay, And Enforcement

Proof/replay:
- `tools/geo/tool_replay_field_geo_window.py`
- field replay hashes now include sampled GEO cell-key identity
- control proof GEO context now carries `field_binding_registry_hash`

Enforcement:
- RepoX
  - `INV-FIELD-STORAGE-GEO-KEYED`
  - `INV-NO-RAW-FIELD-GRID-ASSUMPTION`
- AuditX
  - `E340_RAW_FIELD_GRID_SMELL`
  - `E341_FIELD_SAMPLE_BYPASS_SMELL`

## Readiness For GEO-5

GEO-4 leaves projection/lens concerns out of authoritative field storage. The runtime is now ready for GEO-5 projection and lens work because:
- field values are keyed by topology-aware GEO cells
- frame-aware sampling entry points already exist
- replay/proof surfaces can distinguish field binding context from render-only projection behavior
