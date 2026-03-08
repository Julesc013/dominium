Status: BASELINE
Last Updated: 2026-03-09
Version: 1.0.0
Scope: GEO-2 deterministic reference frames, floating-origin policy, and precision doctrine.

# Reference Frames And Precision

## 1) Purpose

GEO-2 defines the authoritative reference-frame contract used to express positions across very large and very small scales without surrendering deterministic replay or topology portability.

GEO-2 extends, and does not replace:

- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`

This doctrine applies to:

- truth positions
- frame transforms
- render floating-origin rebasing
- field and metric sampling across charts and topologies

## 2) Governing Invariants

- determinism is primary
- authoritative mutation remains process-only
- render and observation remain derived-only
- render rebasing must never mutate truth
- frame transforms must be pure functions of frame graph inputs and profile parameters
- all rounding and overflow behavior must be explicit and TOL-aligned

## 3) FrameGraph

### 3.1 Model

`FrameGraph` is the deterministic graph of coordinate contexts used by truth and GEO queries.

Baseline GEO-2 shape:

- directed rooted tree by default
- DAG only when explicitly declared and still resolvable to a deterministic unique path
- parent chain traversal order is canonical by stable `frame_id`

Canonical baseline examples:

- `frame.galaxy_root`
- `frame.system_root`
- `frame.planet_root`
- `frame.surface_local`
- `frame.interior_local`

### 3.2 Frame node requirements

Each frame node declares:

- `frame_id`
- optional `parent_frame_id`
- `topology_profile_id`
- `metric_profile_id`
- `chart_id`
- `anchor_cell_key`
- `scale_class_id`
- deterministic fingerprint

Each frame is therefore anchored by GEO identity, not by incidental float coordinates.

### 3.3 Anchoring

A frame is anchored by:

- a topology profile
- a metric profile
- a chart inside the topology atlas
- a `geo_cell_key` identifying the stable partition anchor

Implication:

- galaxy frames may anchor at coarse grid cells
- planet frames may anchor at surface atlas tiles
- interior frames may anchor at local partition cells inside authored or procedural charts

### 3.4 Transform edges

Each frame edge declares a deterministic transform to its parent.

Allowed baseline transform kinds in GEO-2:

- `translate`
- `rotate`
- `scale`
- `chart_map_stub`

Transform parameters are fixed-point only.

No transform may depend on:

- wall clock
- thread count
- render state
- camera state
- platform float quirks

## 4) Truth vs Render

### 4.1 TruthModel

Truth stores positions as frame-local references:

- `object_id`
- `frame_id`
- `local_position`

Truth semantics:

- the position is local to its declared frame
- the frame graph provides the only authoritative path to other frames
- truth hashes depend on the position ref and frame graph inputs, not on any render rebase

### 4.2 RenderModel

Render may derive:

- camera-relative coordinates
- floating-origin rebase offsets
- projected view coordinates

Render restrictions:

- render rebasing is presentation-only
- render may not write into truth position state
- render rebasing may not alter replay hashes
- render rebasing may only consume authoritative frame/position inputs and explicit projection requests

### 4.3 Observation and lenses

Projection and render conversion remain epistemically gated:

- truth does not become automatically visible because a frame transform exists
- lens, law, and instrumentation policy still govern what render or map views may request

## 5) Precision Policy

### 5.1 Representation

Positions are stored as fixed-point integer vectors within a declared frame.

GEO-2 baseline policy:

- per-frame local coordinates are fixed-point integers
- scale class determines expected magnitude and safe operating extent
- transforms canonicalize through deterministic rounding rules

### 5.2 Scale classes

Baseline scale classes:

- `galaxy`
- `system`
- `planet`
- `local`

Scale classes are advisory precision policy categories, not runtime mode flags.

### 5.3 Rounding

All transform output rounding must be deterministic and explicit.

Required behavior:

- round only at declared transform boundaries
- use stable integer arithmetic whenever possible
- if division is required, use deterministic rounding policy aligned with TOL
- never rely on host float formatting or locale behavior

### 5.4 Overflow policy

Each frame class must declare maximum safe extents in its transform parameters or extensions.

Overflow handling is deterministic:

- if a transform result exceeds declared safe bounds, the operation refuses or saturates according to declared policy
- overflow behavior must be profile-driven or algorithmically fixed
- silent wrap is forbidden unless the topology explicitly declares wrap semantics

### 5.5 TOL integration

Any bounded approximation must declare:

- tolerance policy id
- bounded error interpretation
- deterministic algorithm id when approximation is used

Examples:

- chart seam mapping stub with bounded integer chart conversion error
- geodesic approximation after frame conversion
- frame chain composition with explicit rounding points

## 6) Cross-Topology Operation

Frames operate inside topology charts.

Implications:

- torus worlds may map through periodic charts
- sphere surface worlds may move between atlas charts
- identified/portal spaces may require chart transition transforms
- future `R^4` stubs may include slice-aware transforms without changing truth semantics

Chart transition rule:

- if `from_frame.chart_id != to_frame.chart_id`, conversion must route through deterministic chart mapping before metric or projection evaluation

## 7) Core GEO-2 Query Contract

### 7.1 `frame_get_transform(from_frame, to_frame)`

Returns:

- deterministic composed transform path between frames
- canonical traversal metadata
- deterministic fingerprint

Rules:

- identical inputs produce identical outputs
- traversal order is canonical
- result is cacheable by `(from_frame_id, to_frame_id, graph_version)`

### 7.2 `position_to_frame(position_ref, target_frame_id)`

Returns:

- converted `position_ref` in the target frame
- chart transition metadata if used
- deterministic fingerprint

Rules:

- conversion composes parent/child transforms in a fixed order
- result is frame-local in the target frame
- no mutation of the source position ref occurs

### 7.3 `position_distance(pos_a_ref, pos_b_ref)`

Returns:

- deterministic distance via frame conversion plus GEO metric evaluation

Rules:

- if positions are in different frames, both are converted through the frame graph first
- metric evaluation uses the resolved topology/metric pair of the comparison frame
- bounded approximation metadata is preserved in extensions where relevant

## 8) Floating-Origin Policy

Floating origin is a render-only policy layer.

### 8.1 Purpose

Floating origin exists to:

- keep render coordinates numerically well-conditioned
- avoid large camera-relative magnitudes in presentation code
- preserve stable truth coordinates and replay hashes

### 8.2 Rules

- choose rebase offset from the camera position or explicit render viewpoint
- derive render-local coordinates by subtracting the deterministic rebase offset
- never write the rebase result back to truth
- rebase output must be reproducible for identical render inputs

### 8.3 Non-semantics

Floating origin does not:

- move authoritative objects
- change frame ownership
- alter topology
- change shard boundaries

## 9) Domain Integration Rules

All domains that need cross-frame spatial semantics must route through GEO-2 APIs for:

- frame conversion
- distance queries
- field sampling position normalization
- render projection entry points

Domains may still use raw local vectors only for declared local micro physics inside a chart.

Forbidden outside that boundary:

- assuming a universal global XYZ truth frame
- comparing unrelated frame-local positions directly
- using render rebase offsets in truth logic

## 10) Sharding And Replay

Cross-shard spatial references remain stable because frames anchor to GEO identities:

- `anchor_cell_key` remains deterministic
- cross-shard references may use `frame_id`, `geo_cell_key`, and stable IDs without raw cross-shard world-space reads

Proof/replay implications:

- frame graph hash chain must be reproducible
- position ref hash chain must be reproducible
- render rebasing is excluded from truth hash semantics

## 11) Baseline GEO-2 Outcome

GEO-2 freezes the following constitutional rule:

- truth position = local fixed-point coordinates in a deterministic frame graph
- render position = derived frame conversion plus optional floating-origin rebase
- cross-frame distance and sampling = GEO query, never ad hoc coordinate arithmetic

This establishes the precision foundation required for:

- galaxy-to-local traversal
- atlas and wrap topologies
- future floating-origin rendering
- later GEO metric/query work in GEO-3
