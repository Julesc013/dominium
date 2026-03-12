Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

## GEO-5 Projection And Lens Model

### Purpose

GEO-5 freezes a single deterministic contract for all geometry-derived views:

- map
- minimap
- atlas unwrap
- slice view
- CCTV snapshot

Every view is derived from three explicit inputs:

1. `ProjectionProfile`
2. `LensRequest`
3. epistemic and instrumentation policy

Rendering remains presentation only. No UI or renderer may read TruthModel directly.

### A. ProjectionRequest

`ProjectionRequest` is the deterministic view geometry request.

Required inputs:

- `projection_profile_id`
- `origin_position_ref`
- `extent_spec`
- `resolution_spec`

Operational context is supplied alongside the request:

- `topology_profile_id`
- `partition_profile_id`
- `metric_profile_id`
- frame graph context when `origin_position_ref` must be rebased into a target frame

Deterministic output is a mapping descriptor plus a bounded ordered cell list:

- projected coordinate mapping descriptor
- ordered `geo_cell_key` list
- per-cell projected coordinates

The engine must enumerate cells deterministically and bound work by request extent and resolution.

### B. LensRequest

`LensRequest` declares which perceived layers may be included in a derived view.

Examples:

- `layer.terrain_stub`
- `layer.temperature`
- `layer.pollution`
- `layer.infrastructure_stub`
- `layer.entity_markers_stub`

`LensRequest` is not authority by itself. It is constrained by:

- `LawProfile`
- epistemic policy
- available instruments
- SIG-delivered receipts where remote sensing is required

Rules:

- unknown data stays hidden
- diegetic sensing may quantize values
- omniscient debug is allowed only through explicit profile/law configuration and must be logged

### C. View Types

#### Map view

- `geo.projection.ortho_2d`
- deterministic cell window over a GEO partition
- suitable for CLI/TUI and GUI adapters

#### Minimap

- same projection contract as map view
- smaller extent or lower resolution
- no special runtime branch

#### Atlas unwrap

- `geo.projection.atlas_unwrap_stub`
- deterministic tile/chart mapping for sphere-surface atlas partitions

#### Slice view

- `geo.projection.slice_nd_stub`
- hyperplane slice over higher-dimensional indexed space
- GEO-5 only requires the bounded deterministic stub

#### CCTV view

- remote camera or map instrument view expressed as a projection plus lens
- view payload is transported as a derived observation artifact over SIG
- delay and loss are transport properties, not renderer behavior

### D. Caching

Derived views are cacheable by:

`H(projection_request, lens_request, truth_hash_anchor, epistemic_policy, version)`

Cache keys must also include any relevant registry hashes:

- projection profile registry hash
- lens-layer registry hash
- view-type registry hash

Caching is valid only because projection and lens derivation are pure functions of their inputs.

### E. Epistemic Gating

Projection alone does not grant visibility.

Visibility rules:

- a view may only include layers present in the resolved lens request
- a diegetic map requires a lawful map/camera instrument channel
- remote CCTV requires SIG-mediated observation delivery
- truth overlays are never promoted into UI unless explicitly allowed by law/profile

### F. Render And UI Boundaries

TruthModel -> PerceivedModel remains the observation boundary.

GEO-5 adds:

PerceivedModel + lawful perceived layer sources -> `projected_view_artifact`

Then:

`projected_view_artifact` -> CLI/TUI/GUI adapter output

Adapters:

- must not query TruthModel
- must not write authoritative state
- must remain deterministic for identical artifacts

### G. Determinism And Replay

Projection and lens derivation must satisfy:

- deterministic ordering
- bounded work
- pure input/output behavior
- stable canonical hashes across repeated runs and platforms

Replay regenerates identical `projected_view_artifact` payloads from:

- the same perceived inputs
- the same projection request
- the same lens request
- the same registry hashes

### H. Non-Goals

GEO-5 does not implement:

- advanced GPU pipelines
- real video streaming
- direct truth reads in UI
- nondeterministic camera effects
- wall-clock-dependent refresh logic
