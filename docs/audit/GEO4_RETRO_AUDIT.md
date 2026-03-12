Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO-4 Retro Audit

Status: AUDIT
Last Updated: 2026-03-09
Scope: GEO-4 field storage, sampling, and partition-binding audit for GEO-bound field semantics.

## 1) Audit Goal

Identify current FIELD storage and sampling assumptions that still treat `cell_id` or cartesian-grid addressing as the canonical field-space contract.

Relevant governing invariants:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`
- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`
- `docs/geo/METRIC_QUERY_ENGINE.md`

## 2) FIELD Storage Layout Audit

### 2.1 Canonical field row storage today

Files found:

- `src/fields/field_engine.py`
- `schema/fields/field_cell.schema`
- `schema/fields/field_layer.schema`

Observed assumptions:

- field storage rows are normalized by `(field_id, cell_id)`
- `build_field_cell(...)` requires a raw `cell_id` string and does not require a structured `geo_cell_key`
- `normalize_field_cell_rows(...)` sorts by `cell_id`, not by partition-aware key semantics
- `get_field_value(...)` samples by resolving a string `sampled_cell_id` and then looking up `field_id::cell_id`
- `update_field_layers(...)` builds and updates field cells by raw `cell_id`

Assessment:

- FIELD already has a GEO seam through `geo_partition_cell_key(...)`
- FIELD still treats legacy string cell aliases as canonical storage identity
- this blocks geometry-agnostic storage because atlas, torus, and future tree partitions are only represented indirectly through alias strings

Migration notes:

- make structured `geo_cell_key` the canonical field address
- keep `cell_id` as deterministic legacy alias / compatibility surface
- normalize update and lookup ordering by canonical GEO cell-key ordering rather than alias string ordering

### 2.2 Field layer binding today

Files found:

- `src/fields/field_engine.py`
- `data/registries/field_type_registry.json`
- `data/registries/field_update_policy_registry.json`

Observed assumptions:

- layer bindings to topology/partition live only in ad hoc layer `extensions`
- there is no first-class registry declaring which field binds to which GEO partition/profile pair
- interpolation policy is implicit nearest-cell behavior

Assessment:

- FIELD lacks a first-class GEO binding contract
- default behavior is already deterministic, but not yet profile-registered

Migration notes:

- add canonical `field_binding` and `interpolation_policy` schema/registry surfaces
- let layer extensions override only where lawful, but keep binding identity in data registries

## 3) Field Sampling Audit

### 3.1 Current `field.sample` behavior

Files found:

- `src/fields/field_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

Observed assumptions:

- `get_field_value(...)` accepts `spatial_position`, not `position_ref`
- `_field_cell_id_for_position(...)` returns a string alias from explicit `cell_id` or `geo_partition_cell_key(...)`
- sampling is effectively nearest-cell lookup with fallback to `field.default`
- sample caching is keyed by `field_id::spatial_node_id::tick`

Assessment:

- nearest-cell semantics are stable and should remain the default compatibility path
- sampling still collapses GEO identity into a legacy alias string before storage lookup
- GEO-2 frame-aware `position_ref` sampling exists as an adapter seam but is not yet the canonical FIELD query

Migration notes:

- add canonical FIELD sampling by `geo_cell_key`
- add deterministic `position_ref -> geo_cell_key -> sample` flow
- preserve nearest-cell default semantics for default `r3_infinite + grid_zd`

### 3.2 FIELD falloff / neighborhood behavior

Observed assumptions:

- there is no general field neighborhood sampling API in FIELD yet
- future radius/falloff behavior would otherwise drift into domain-local logic

Migration notes:

- add canonical neighborhood sampling routed through `geo_neighbors(...)`
- keep interpolation stubbed to nearest-cell / atlas-nearest in GEO-4

## 4) POLL Dispersion Audit

Files found:

- `src/pollution/dispersion_engine.py`

Observed assumptions:

- POLL already routes neighbor iteration through `geo_neighbors(...)`
- concentration and wind maps are still keyed by `cell_id` strings from field rows
- POLL assumes those aliases are stable enough to serve as concentration-cell identity

Assessment:

- GEO-3 already solved the neighborhood seam
- GEO-4 must now let POLL consume field rows whose canonical address is `geo_cell_key`

Migration notes:

- make POLL field-row indexing prefer canonical GEO cell keys while retaining alias compatibility
- keep `spatial_scope_id` / `cell_id` compatibility strings for existing source-event surfaces

## 5) THERM Ambient Coupling Audit

Files found:

- `src/thermal/network/thermal_network_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

Observed assumptions:

- thermal network solver consumes direct `ambient_temperature` and `ambient_temperature_by_node` inputs
- vehicle/interior boundary exchange samples external temperature, moisture, wind, and visibility through `get_field_value(...)`
- those boundary samples are driven by raw sample positions plus optional `field_cell_id` alias

Assessment:

- the thermal solver itself is not yet FIELD-bound
- the boundary-exchange seam is the cleanest GEO-4 integration point for ambient field sampling

Migration notes:

- add an explicit GEO-bound field boundary exchange helper
- allow THERM-facing ambient sampling to use FIELD nearest-cell sampling over GEO cell keys and optional `position_ref`
- do not rewrite the thermal solver into a PDE or climate engine

## 6) Required Refactors For GEO Cell-Key Binding

Highest-value GEO-4 refactors:

1. canonicalize field storage identity as `geo_cell_key`
2. keep `cell_id` as deterministic legacy alias only
3. introduce first-class `field_binding` and interpolation registries
4. sort field update iteration by canonical GEO cell-key ordering
5. route boundary exchange artifacts through GEO-keyed field samples

Deferred beyond GEO-4:

- richer interpolation beyond nearest-cell / atlas-nearest stubs
- full thermal/climate field solver coupling
- octree field update logic beyond schema/runtime stubs
- broad migration of all legacy `spatial_scope_id` domain records to structured GEO identity

## 7) Audit Outcome

The current repo already has the right seams:

- GEO partition mapping exists
- GEO metric neighborhoods exist
- process-driven field mutation already exists

The remaining portability risk is that FIELD storage identity is still effectively `field_id + cell_id`.

GEO-4 should therefore:

- freeze GEO-bound field bindings in data
- make `geo_cell_key` canonical inside FIELD runtime
- keep existing R3 nearest-cell behavior stable through deterministic alias compatibility
