# Field Binding To GEO

Status: CANONICAL
Last Updated: 2026-03-09
Scope: GEO-4 doctrine for GEO-bound field storage, sampling, updates, and shard exchange.

## 1) Purpose

GEO-4 freezes the canonical contract that binds FIELD storage and sampling to GEO partition and topology semantics.

GEO-4 extends, and does not replace:

- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`
- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`
- `docs/geo/METRIC_QUERY_ENGINE.md`

## 2) Governing Invariants

- determinism is primary
- authoritative field mutation remains process-only
- field storage identity is profile-driven, not hardcoded to cartesian grids
- field sampling is geometry-agnostic and routes through GEO partition and metric APIs
- cross-shard field exchange uses deterministic boundary artifacts keyed by GEO identity

## 3) Core Normative Rule

FIELD does not own space.

FIELD binds to GEO-declared topology and partition profiles, and field values are canonically addressed by `geo_cell_key`.

Legacy `cell_id` strings may remain as compatibility aliases, but they are not the canonical spatial identity surface after GEO-4.

## 4) Field Storage Domains

### 4.1 Canonical binding

Each `FieldType` binds through a `field_binding` contract that declares:

- `field_id`
- `topology_profile_id`
- `partition_profile_id`
- `storage_kind`
- `interpolation_policy_id`

### 4.2 Supported baseline storage kinds

- `cell`
  for deterministic `Z^D` grid partitions
- `tile`
  for atlas and sphere-surface tile partitions
- `octree_stub`
  reserved deterministic tree-node addressing without claiming full octree solver support

### 4.3 Canonical address

The canonical field address is:

- `field_id`
- semantic `geo_cell_key`

Compatibility alias:

- `cell_id`

Rule:

- `cell_id` may serialize the legacy alias for existing callers
- `geo_cell_key` remains the canonical runtime identity for ordering, lookup, proof, and replay

## 5) Sampling

### 5.1 Canonical queries

FIELD must expose geometry-agnostic sampling surfaces for:

- sample at `position_ref`
- sample at `geo_cell_key`
- sample over a GEO neighborhood

### 5.2 Position sampling

`sample(position_ref)` performs:

1. resolve the target field frame and chart using GEO-2
2. map the resulting position to `geo_cell_key` using GEO-1 partition mapping
3. apply the declared interpolation policy
4. return sampled value plus sampled GEO cell identity

### 5.3 Cell sampling

`sample(cell_key)` performs:

- direct deterministic lookup by semantic `geo_cell_key`
- compatibility fallback by legacy alias only when canonical key metadata is absent

### 5.4 Neighborhood sampling

Neighborhood field queries must use:

- `geo_neighbors(center_cell_key, radius, ...)`

Never:

- hand-written coordinate stepping
- raw grid-only offset logic in domain code

## 6) Interpolation Policy

### 6.1 Baseline policies

- `interp.nearest`
  canonical GEO-4 default
- `interp.bilinear_stub`
  reserved deterministic 2D blending contract
- `interp.atlas_nearest`
  nearest-tile sampling across atlas charts

### 6.2 GEO-4 default

GEO-4 preserves existing default field behavior through:

- nearest-cell sampling for default `r3_infinite + grid_zd`
- deterministic alias compatibility for existing `cell.*` callers

### 6.3 Determinism rule

Interpolation policy must declare:

- deterministic algorithm
- bounded neighborhood requirement when relevant
- TOL-compatible rounding for outputs

## 7) Updates

### 7.1 Field update policy

PHYS-2 field update policy remains the law for *what* updates do.

GEO-4 changes *where* and *in what order* they operate:

- field updates iterate over canonical GEO cell keys
- update ordering is deterministic by canonical GEO cell-key ordering
- atlas/tile partitions use chart-first, index-tuple-second ordering

### 7.2 Compatibility rule

For default R3 grid profiles, GEO-4 must preserve the same effective nearest-cell behavior and stable update outcomes as pre-GEO-4 FIELD.

### 7.3 Coupling relevance

Field changes beyond tolerance must continue to mark relevant couplings, but the relevance walk is now over GEO-bound cell identities rather than raw alias assumptions.

## 8) Shard Boundaries

Cross-shard field exchange uses boundary artifacts keyed by:

- `field_id`
- `geo_cell_key`
- deterministic sampled values

Rules:

- no direct cross-shard field-row reads
- no ambient field access by raw coordinates across shard boundaries
- boundary artifact ordering is deterministic

## 9) Domain Obligations

Domains consuming fields must use FIELD + GEO surfaces for:

- POLL dispersion and exposure sampling
- THERM ambient boundary sampling
- PHYS gravity/radiation field lookup
- ROI and activation field-related cell targeting

Forbidden:

- raw cartesian field-index arithmetic in domain code
- assuming `cell_id` string shape as the canonical geometry contract
- direct field lookup by ad hoc grid math outside FIELD / GEO

## 10) Proof And Replay

Proof surfaces using GEO-bound fields should include:

- `field_binding_registry` hash
- field update hash chain keyed by canonical GEO field addresses
- field sample hash chain including sampled GEO identity
- boundary field exchange hash chain keyed by GEO cell identity

Replay equivalence requires identical results for identical:

- field bindings
- interpolation policies
- GEO profiles
- field update inputs
- boundary artifacts

## 11) Baseline GEO-4 Outcome

After GEO-4:

- FIELD stores values against GEO cell identity instead of raw grid assumptions
- nearest-cell remains the default compatibility behavior
- atlas/tile and future tree partitions become lawful field-storage domains
- shard-safe field exchange is GEO-keyed and replay-stable

This establishes the substrate required for GEO-5 projection and lens-facing field presentation.
