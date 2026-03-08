# GEO-0 Retro Consistency Audit

Status: DERIVED
Last Updated: 2026-03-08
Scope: GEO-0 pre-migration audit of existing spatial assumptions.

## Purpose

Identify current direct spatial assumptions that will need to route through the Geometry Kernel once GEO-0 is in force.

This audit does not apply migrations. It records concrete call sites, assumptions, and follow-up targets.

## Constitutional References

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` E2 Deterministic ordering
- `docs/canon/constitution_v1.md` E7 Hash-partition equivalence
- `docs/canon/glossary_v1.md` Space
- `docs/canon/glossary_v1.md` Lens
- `docs/canon/glossary_v1.md` UniverseIdentity

## Audit Summary

Current code is still mostly authored around implicit `R^3` Cartesian assumptions:

- cell IDs frequently assume `x/y/z` integer axes
- distance heuristics often assume direct component arithmetic
- camera/render projection assumes a local Euclidean perspective pipeline
- mobility micro integrates local coordinates directly with corridor/volume clamps

These assumptions are deterministic today, but they are not geometry-portable. GEO-0 needs to centralize:

- neighbor enumeration
- distance queries
- coordinate transforms between charts
- projection and slice requests
- partition-derived cell keys

## Findings By Area

### 1. MOB movement and ROI

#### Local micro physics still assumes direct XYZ vectors

File:
- `src/mobility/micro/free_motion_solver.py`

Observed pattern:
- velocity, momentum, acceleration, and position updates are integrated directly over `x/y/z`
- corridor and volume enforcement clamp against axis-aligned bounds

Assessment:
- acceptable as local micro physics inside a declared chart
- not acceptable as the global geometry contract for cross-chart, wrapped, spherical, portal, or identified spaces

Migration note:
- preserve local chart-frame integration
- route chart/boundary interpretation through `SpaceTopologyProfile` and chart transforms
- route non-Euclidean distance/neighbor decisions outside the local solver through GEO APIs

#### ROI scheduling is not yet geometry-driven

File:
- `src/system/roi/system_roi_scheduler.py`

Observed pattern:
- ROI activation is keyed by system IDs, tiers, and scheduler state rather than geometric neighborhood queries

Assessment:
- no direct XYZ arithmetic found in current scheduler
- future spatial ROI refinement must bind to `GeometryPartitionProfile` rather than introducing ad hoc region math

Migration note:
- add GEO-backed partition/adjacency requests when ROI selection becomes spatial

### 2. FIELD sampling

#### Field cell selection hardcodes 3D Cartesian partitioning

File:
- `src/fields/field_engine.py`

Observed pattern:
- `_field_cell_id_for_position()` reads `x/y/z`
- divides by `cell_size_mm`
- emits `cell.{cx}.{cy}.{cz}`

Assessment:
- deterministic, but assumes:
  - fixed 3D dimension
  - single Cartesian chart
  - grid partition
  - no topology transform/wrap/portal identification

Migration note:
- replace direct cell-key derivation with GEO partition helpers
- allow topology/partition profiles to define canonical cell keys for `Z^D`, atlas tiles, or identified spaces

### 3. POLL dispersion

#### Dispersion uses direct neighbor lists and direct wind XYZ magnitude

File:
- `src/pollution/dispersion_engine.py`

Observed pattern:
- neighbor iteration uses `neighbor_map`
- wind bias strength uses `abs(x) + abs(y) + abs(z)`
- implicit assumption that diffusion neighborhood lives in a simple Cartesian adjacency model

Assessment:
- deterministic today
- not geometry-portable across torus, spherical atlas, portal face identification, or higher-dimensional spaces

Migration note:
- route neighbor enumeration through GEO neighbor queries when authoritative topology is active
- route metric-sensitive bias terms through GEO distance/measure conventions where needed
- keep pollutant update law separate from topology lookup

### 4. SYS ROI scheduling

#### No direct coordinate arithmetic found in current ROI scheduler

File:
- `src/system/roi/system_roi_scheduler.py`

Observed pattern:
- scheduling currently uses deterministic system/priority state, not raw positions

Assessment:
- no immediate GEO-0 refactor required
- scheduling will need a GEO partition integration point when spatial ROI activation/refinement is introduced

Migration note:
- define a future SRZ-safe GEO partition query interface for ROI refinement and shard boundary artifacts

### 5. Rendering and camera

#### LOD distance assumes Manhattan-like XYZ origin distance

File:
- `src/client/render/representation_resolver.py`

Observed pattern:
- `_lod_hint_for_candidate()` computes distance as `abs(x) + abs(y) + abs(z)`

Assessment:
- deterministic but not metric-portable
- unsuitable for wrapped, spherical, portal, or atlas spaces

Migration note:
- route LOD distance through `geo_distance()`
- use universe-bound topology and metric defaults or explicit projection-lens context

#### Software renderer assumes direct Euclidean camera transform and projection

File:
- `src/client/render/renderers/software_renderer.py`

Observed pattern:
- `_camera_space()` subtracts object and camera `x/y/z`
- `_project_point()` performs direct perspective projection

Assessment:
- valid as one projection implementation
- invalid as the only render-space contract

Migration note:
- move canonical projection request through `geo_project()`
- retain renderer-local rasterization after projection
- keep projection epistemically gated through lens/instrumentation context

## Direct XYZ Arithmetic Migration Targets

Priority GEO migration targets:

1. `src/fields/field_engine.py`
- replace raw `cell.{cx}.{cy}.{cz}` derivation with GEO partition cell-key derivation

2. `src/client/render/representation_resolver.py`
- replace direct LOD distance heuristic with `geo_distance()`

3. `src/client/render/renderers/software_renderer.py`
- replace direct camera/project pipeline with `geo_project()`

4. `src/pollution/dispersion_engine.py`
- allow deterministic GEO neighborhood routing instead of purely local `neighbor_map` assumptions

Deferred but tracked:

5. `src/mobility/micro/free_motion_solver.py`
- keep local chart-frame micro integration
- later bind corridor/volume/boundary interpretation to topology/chart declarations

6. `src/system/roi/system_roi_scheduler.py`
- no current direct XYZ arithmetic
- future ROI refinement should consume GEO partition queries

## Required GEO-0 Migration Interfaces

The following interfaces are required to absorb the assumptions above without refactor churn:

- `geo_neighbors(cell_key, topology_profile_id, radius, metric_profile_id)`
- `geo_distance(pos_a, pos_b, topology_profile_id, metric_profile_id)`
- `geo_transform(pos, from_chart, to_chart)`
- `geo_project(pos, topology_profile_id, projection_profile_id)`
- deterministic partition-to-cell helper for field/grid lookup

## Non-Goals For This Audit

- no solver rewrites
- no pathfinding
- no geometry authoring
- no world generation
- no migration of all legacy local chart math

## Conclusion

The repository is deterministic but still structurally biased toward implicit Cartesian `R^3`.

GEO-0 should therefore:

- freeze a first-class geometry contract before more domains bake in coordinate assumptions
- preserve local chart-frame micro physics where appropriate
- move authoritative topology, metric, partition, and projection semantics into shared GEO APIs
