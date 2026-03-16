Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: GEO-2 retro-consistency audit for reference frames, floating origin, and precision policy.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# GEO2 Retro Audit

## 1) Purpose

This audit records the current pre-GEO-2 coordinate assumptions that still exist across movement, camera, field sampling, ROI scheduling, observation, and rendering.

GEO-2 remains additive in this phase:

- no domain migrations are performed here
- no truth tick ordering changes are introduced here
- no render rebasing is allowed to leak into truth

Relevant governing constraints:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A3 Observer/renderer/truth separation
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`

## 2) Summary

Current runtime state already uses fixed-point integer coordinates widely, which is compatible with GEO-2, but those coordinates are still interpreted mostly as raw frame-less `position_mm{x,y,z}` values.

The main gaps are:

- truth positions are not yet represented as canonical `position_ref(frame_id + local_position)`
- frame transforms are not centrally resolved through a deterministic GEO frame graph
- ROI and observation still use distance-from-origin heuristics instead of frame-aware position distances
- render code still subtracts camera position directly rather than rebasing through a dedicated render-only floating-origin policy

## 3) Current Assumptions By Area

| Area | Current surface | Current assumption | GEO-2 implication |
| --- | --- | --- | --- |
| MOB movement | `tools/xstack/sessionx/process_runtime.py` | `process.camera_move` and `process.agent_move` mutate raw `position_mm` vectors and derive distances from component sums | Truth positions need frame-local refs; local micro motion may stay local but frame conversion must move to GEO |
| Camera / freecam | `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/process_runtime.py`, `tools/xstack/sessionx/observation.py` | camera stores `frame_id` plus raw `position_mm`; teleport and viewpoint logic treat the frame as a label, not a transform graph anchor | camera truth needs a stable `position_ref`; render rebasing must stay derived-only |
| Field sampling | `src/fields/field_engine.py` | field lookup partitions raw positions to legacy string `cell_key` aliases | field sampling needs a frame-aware adapter that first resolves into the correct frame/chart and then partitions |
| Pollution dispersion | `src/pollution/dispersion_engine.py` | neighbor iteration is already GEO-routed, but the surrounding field state still uses legacy cell ids | GEO-2 does not need to refactor dispersion, but future sampling inputs should carry frame-aware cell provenance |
| ROI scheduling | `tools/xstack/sessionx/process_runtime.py`, `src/system/roi/system_roi_scheduler.py` | ROI tiering relies on Manhattan distance from camera origin or pre-authored anchor distances | GEO distance must replace origin heuristics where the query crosses frames/topologies |
| Rendering | `src/client/render/representation_resolver.py`, `src/client/render/renderers/software_renderer.py` | LOD uses GEO distance in one spot, but render conversion still subtracts camera/object XYZ directly | render conversion needs a dedicated floating-origin adapter that never mutates truth |
| Core spatial hierarchy | `src/core/spatial/spatial_engine.py` | local transforms compose deterministically, but only within a local spatial-node hierarchy and fixed R3 vector layout | GEO-2 frame graph can coexist with this helper but should become the canonical cross-scale frame surface |

## 4) Concrete Hotspots

### 4.1 MOB movement and local physics

Observed surfaces:

- `tools/xstack/sessionx/process_runtime.py`
  - `process.camera_move` directly increments `camera["position_mm"]`
  - `process.agent_move` derives `world_delta` and writes movement metadata from raw XYZ deltas
  - movement distance is summarized as `abs(x)+abs(y)+abs(z)`

Assessment:

- local micro movement inside a declared chart is still acceptable as local physics
- the missing piece is a canonical `position_ref` wrapper and a frame transform lookup for any cross-frame or cross-chart query

Required GEO-2 migration notes:

- camera truth should be representable as `position_ref`
- agent/body movement helpers should accept or emit frame-aware position refs at the adapter boundary
- raw distance summaries in control metadata should route through frame-aware helper functions when semantics are "distance", not "delta magnitude"

### 4.2 Camera / navigation / freecam

Observed surfaces:

- `tools/xstack/sessionx/creator.py`
  - default camera is seeded as `frame_id + position_mm + orientation_mdeg`
- `tools/xstack/sessionx/process_runtime.py`
  - teleport target resolution returns raw `frame_id` and `position_mm`
  - site/object teleports treat `frame_id` as a direct target token
- `tools/xstack/sessionx/observation.py`
  - `camera_viewpoint` copies camera truth position into perceived/render surfaces

Assessment:

- the current camera model already distinguishes frame identity from local coordinates, which is a good GEO-2 anchor
- however, the frame is not yet backed by a deterministic transform graph, so cross-scale traversal still depends on ad hoc interpretation

Required GEO-2 migration notes:

- introduce canonical `frame_node` / `frame_transform` / `position_ref` surfaces without breaking existing camera payloads
- keep camera mutation process-only
- keep render rebasing derived from the camera viewpoint, never from truth mutation

### 4.3 Field sampling

Observed surface:

- `src/fields/field_engine.py`
  - `_field_cell_id_for_position(...)` already routes through `geo_partition_cell_key(...)`
  - the return value is still a legacy string cell key

Assessment:

- this is the cleanest migration seam in the current repo
- GEO-2 does not need to rewrite field storage, but it should add a frame-aware adapter so callers can sample via `position_ref -> target frame/chart -> cell key`

Required GEO-2 migration notes:

- add GEO frame adapter helpers for field sampling requests
- preserve existing field value semantics and deterministic partitioning
- defer full replacement of legacy string cell ids to a later migration task

### 4.4 ROI scheduling

Observed surfaces:

- `src/system/roi/system_roi_scheduler.py`
  - scheduler is system-centric and does not perform spatial math itself
- `tools/xstack/sessionx/process_runtime.py`
  - `_camera_distance_mm(...)` computes Manhattan distance from absolute camera origin
  - ROI and cohort refinement logic uses that scalar distance as a proxy for fidelity selection

Assessment:

- scheduling policy itself is not the problem; the distance source is
- origin-distance heuristics are not topology-safe and will fail for torus/sphere/multi-frame worlds

Required GEO-2 migration notes:

- add a GEO frame distance adapter for ROI thresholds
- keep tier ordering and policy semantics unchanged
- later ROI migrations should replace origin-based heuristics with `position_distance(...)` between frame-aware anchors

### 4.5 Observation / epistemic precision

Observed surface:

- `tools/xstack/sessionx/observation.py`
  - `_camera_distance_mm(...)` reads `camera_viewpoint.position_mm` and computes Manhattan distance from origin
  - precision rules and population quantization branch on that derived distance

Assessment:

- observation remains derived, which is correct
- but the current precision heuristic assumes a single global origin and does not use frame-relative distance to an observed target or chart

Required GEO-2 migration notes:

- observation precision should consume frame-aware distance helpers once targets and viewpoints are both representable as `position_ref`
- render/viewpoint rebasing must remain observation/render-only

### 4.6 Rendering and camera-relative conversion

Observed surfaces:

- `src/client/render/representation_resolver.py`
  - LOD hint selection already uses `geo_distance(...)`
- `src/client/render/renderers/software_renderer.py`
  - `geo_project(...)` is used for final projection
  - legacy `_camera_space(...)` and `_project_point(...)` helpers still exist and perform direct camera-relative subtraction/rotation

Assessment:

- GEO-0 succeeded in getting projection and one LOD path onto GEO
- GEO-2 still needs an explicit floating-origin policy object so render rebasing is named, deterministic, cacheable, and isolated from truth

Required GEO-2 migration notes:

- render conversion should use a GEO render-only rebasing helper
- add a guard that render conversion cannot write back into truth position surfaces
- preserve current projection behavior while routing large-scale coordinate rebasing through GEO

### 4.7 Core spatial hierarchy

Observed surface:

- `src/core/spatial/spatial_engine.py`
  - deterministic parent-chain transform composition exists for `SpatialNode`

Assessment:

- this is compatible with GEO-2 but not sufficient by itself
- it composes local transforms, not topology-aware chart/frame transforms anchored by GEO cell keys

Required GEO-2 migration notes:

- retain `SpatialNode` composition for local authored hierarchies
- add GEO frame graph as the canonical cross-scale frame API
- bridge only through adapters; do not silently reinterpret `SpatialNode` as GEO truth

## 5) Where A Frame Graph Is Needed

Frame graph required:

- camera truth and render viewpoints
- galaxy -> system -> planet -> local/interior anchor relationships
- cross-chart topology transitions
- ROI distance decisions across nonlocal anchors
- field sampling requests that cross authored chart or frame boundaries

Raw local coordinates may remain acceptable inside a declared chart:

- micro collision / local movement deltas
- local authored interior offsets
- local renderer staging after a floating-origin rebase has already been derived from truth

## 6) Migration Targets For Later Phases

These are notes only for future migration work:

1. Replace camera truth storage from raw `frame_id + position_mm` semantics to canonical `position_ref` semantics while preserving compatibility fields.
2. Route ROI distance heuristics through GEO frame distance helpers.
3. Route observation precision distance heuristics through GEO frame distance helpers.
4. Route field sampling entry points through `position_ref -> frame transform -> partition` adapters.
5. Replace render-local camera subtraction helpers with a GEO floating-origin conversion surface.
6. Add canonical frame graph/profile metadata into proof surfaces whenever frame-aware positions participate in a session.

## 7) GEO-2 Phase Boundary

This audit indicates GEO-2 can proceed without canon conflict because:

- fixed-point local coordinates already exist
- `frame_id` already exists in several truth and authored surfaces
- GEO-1 cell identity already provides stable anchors for frame nodes

The work required in GEO-2 is therefore constitutional and adapter-oriented, not a repo-wide movement rewrite.
