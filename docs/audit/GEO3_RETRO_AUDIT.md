Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO-3 Retro Audit

Status: AUDIT
Last Updated: 2026-03-09
Scope: GEO-3 metric query engine migration audit for direct distance, geodesic, and neighborhood usage.

## 1) Audit Goal

Identify pre-GEO-3 distance and neighborhood assumptions that must route through the canonical metric query engine.

Relevant governing invariants:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`

## 2) Direct Distance Usage Audit

### 2.1 MOB movement and geometry helpers

Files found:

- `src/mobility/micro/constrained_motion_solver.py`
- `src/mobility/geometry/geometry_engine.py`

Observed assumptions:

- `constrained_motion_solver.py` computes guide-length accumulation with direct `dx/dy/dz` arithmetic and `math.sqrt(...)`.
- `geometry_engine.py` computes path length and curvature summaries with direct integer XYZ arithmetic and `math.isqrt(...)`.

Assessment:

- These are local micro / guide-geometry calculations, not world-topology queries.
- They are still raw Euclidean assumptions and should eventually route through GEO metric helpers for segment length inside a declared chart.

Migration notes:

- add a GEO-local segment-distance helper for chart-declared micro geometry
- replace direct segment length accumulation in constrained motion and guide geometry metrics once the GEO metric surface stabilizes
- keep curvature-only vector algebra local for now; GEO-3 does not need to rewrite local turning geometry

### 2.2 Rendering and camera

Files found:

- `src/client/render/representation_resolver.py`
- `src/client/render/renderers/software_renderer.py`

Observed assumptions:

- `representation_resolver.py` already routes LOD distance through `geo_distance(...)`.
- `software_renderer.py` still performs local camera-space transforms and raster math after `geo_project(...)`.

Assessment:

- representation distance is already compliant
- software renderer math is presentation-local and does not need GEO metric routing

Migration notes:

- no GEO-3 migration required for renderer-local raster math
- keep projection entry through `geo_project(...)`

### 2.3 FIELD sampling

Files found:

- `src/fields/field_engine.py`

Observed assumptions:

- field cell addressing already routes through `geo_partition_cell_key(...)`
- no direct Euclidean distance or `sqrt(...)` use found in field sampling
- no field falloff kernel currently computes raw distance in this module

Assessment:

- FIELD is already on the correct partition seam
- GEO-3 should provide a canonical falloff-distance helper for future field kernels

Migration notes:

- future field falloff or radius sampling must use GEO metric APIs or GEO neighborhood enumeration
- existing field lookup path can remain unchanged in GEO-3

### 2.4 POLL dispersion

Files found:

- `src/pollution/dispersion_engine.py`

Observed assumptions:

- dispersion already calls `geo_neighbors(...)`
- concentration diffusion uses neighbor deltas, not raw coordinate distance
- no direct Euclidean distance or `sqrt(...)` use found

Assessment:

- POLL already has the correct neighborhood-routing seam
- GEO-3 should upgrade the public `geo_neighbors(...)` path so POLL automatically inherits canonical partition-aware ordering and caps

Migration notes:

- keep `evaluate_pollution_dispersion(...)` on GEO neighbor iteration
- no domain rewrite required beyond using the GEO-3 neighborhood engine behind the API

### 2.5 SYS ROI scheduling

Files found:

- `src/system/roi/system_roi_scheduler.py`

Observed assumptions:

- current scheduler does not compute spatial distances directly
- ROI membership arrives as preselected ID sets rather than metric queries

Assessment:

- there is no raw Euclidean distance smell in current scheduler code
- GEO-3 still needs a canonical ROI-distance seam for future radius-based scheduling inputs

Migration notes:

- future ROI radius checks must route through `roi_distance_mm(...)` or `geo_distance(...)`
- GEO-3 should add a narrow domain adapter for ROI metric queries even if the scheduler is not yet consuming it directly

## 3) Confirmed GEO-Compliant Hooks

Already compliant:

- `src/client/render/representation_resolver.py` uses `geo_distance(...)`
- `src/fields/field_engine.py` uses `geo_partition_cell_key(...)`
- `src/pollution/dispersion_engine.py` uses `geo_neighbors(...)`

Partially compliant / still local-math:

- `src/mobility/micro/constrained_motion_solver.py`
- `src/mobility/geometry/geometry_engine.py`

## 4) Migration Priority

Highest priority for GEO-3 enforcement:

1. freeze canonical GEO metric APIs for distance, geodesic, and neighborhood queries
2. add a domain-facing GEO metric adapter surface for ROI, FIELD falloff, and POLL neighborhood access
3. fence new raw distance usage with RepoX and AuditX

Deferred beyond GEO-3:

- full migration of existing local guide-geometry length math in MOB
- replacement of renderer-local camera-space math
- topology-aware curvature metrics for authored paths

## 5) Audit Outcome

The current repo already has good GEO seams for:

- render LOD distance
- field partition sampling
- pollution neighborhood iteration

The remaining portability risk is concentrated in local MOB geometry helpers where raw XYZ segment length still appears. GEO-3 should therefore:

- provide the canonical metric engine
- expose a domain adapter layer that future domain code must use
- enforce a ratchet against new ad hoc distance calculations
