Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: GEO-10 stress, proof, replay, overlay identity, degradation, and regression lock baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO Final Baseline

## 1) Scope

GEO-10 freezes the full GEO envelope after GEO-0 through GEO-9:

- pluggable topology, metric, partition, and projection profiles
- stable geo cell keys and object identities
- deterministic frame transforms and render-only floating origin
- metric and neighborhood queries
- GEO-bound fields
- projection and lens views
- deterministic pathing
- geometry edits with provenance and replay
- worldgen version locking and deterministic overlays

The authoritative contracts are:

- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`
- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`
- `docs/geo/METRIC_QUERY_ENGINE.md`
- `docs/geo/FIELD_BINDING_TO_GEO.md`
- `docs/geo/PROJECTION_AND_LENS_MODEL.md`
- `docs/geo/PATHING_AND_TRAVERSAL_MODEL.md`
- `docs/geo/GEOMETRY_EDIT_CONTRACT.md`
- `docs/geo/WORLDGEN_CONSTITUTION.md`
- `docs/geo/OVERLAY_MERGE_CONSTITUTION.md`

Relevant invariants upheld:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A6 Provenance is mandatory
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` A9 Pack-driven integration
- `docs/canon/constitution_v1.md` A10 Explicit degradation and refusal
- `INV-GEO-BUDGETED`
- `INV-OVERLAY-MERGE-DETERMINISTIC`
- `INV-NO-TRUTH-IN-UI`
- `INV-GEO-ID-STABLE`

## 2) Topology Suite Coverage

The fixed-seed GEO-10 scenario is `scenario.geo10.stress.0615b5464e6f` with seed `91017`.

Covered suites:

- `geo10.suite.r3_grid`: `geo.topology.r3_infinite` + `geo.metric.euclidean` + `geo.partition.grid_zd` + `geo.projection.perspective_3d`
- `geo10.suite.r2_factorio`: `geo.topology.r2_infinite` + `geo.metric.euclidean` + `geo.partition.grid_zd` + `geo.projection.ortho_2d`
- `geo10.suite.torus_r2`: `geo.topology.torus_r2` + `geo.metric.torus_wrap` + `geo.partition.grid_zd` + `geo.projection.ortho_2d`
- `geo10.suite.sphere_atlas`: `geo.topology.sphere_surface_s2` + `geo.metric.spherical_geodesic_stub` + `geo.partition.atlas_tiles` + `geo.projection.atlas_unwrap_stub`
- `geo10.suite.cube_portal`: `geo.topology.cube_identified_stub` + portal adjacency + `geo.partition.grid_zd` + `geo.projection.ortho_2d`
- `geo10.suite.r4_slice`: `geo.topology.r4_stub` + `geo.metric.euclidean` + `geo.partition.grid_zd` + `geo.projection.slice_nd_stub`

Each suite exercises:

- frame graph traversal and render rebasing
- field sampling and pollution surfaces
- lens-gated projected views
- deterministic A* pathing
- geometry edits plus compaction replay
- worldgen base layer plus overlay merge

## 3) Stress Metrics

Aggregate baseline metrics from `build/geo/geo10_stress_report.json`:

- metric queries: `36`
- metric cache hits: `18`
- metric cache hit rate: `500` permille
- neighbor enumerations: `6`
- projected view cells: `405`
- lens redactions: `810`
- path expansions: `140`
- geometry edit events: `24`
- overlay merges: `6`
- compaction markers: `6`
- degradation count: `0`

Baseline report fingerprint:

- stress report fingerprint: `f5ae8f33f24e4576e4ec5159193a96cb5ce5819eba6cfe1facb1094306bc1955`
- cross-platform determinism hash: `c1480f8970a6df0d918ad2718d188901e88160ae91734af70114b5766a5cde39`

## 4) Degradation Behavior

Deterministic degradation order is frozen as:

1. `reduce_projection_resolution`
2. `reduce_neighbor_radius_noncritical`
3. `reduce_path_expansion_cap`
4. `defer_derived_view_generation`
5. `preserve_canonical_geometry_and_overlay`

Baseline run did not require degradation, but the order and explain surfaces are locked through:

- `src/geo/degradation_policy.py`
- `explain.view_downsampled`
- `explain.path_refused_budget`

Canonical guarantees preserved even under degrade pressure:

- geometry edit events are never skipped
- overlay patches are never skipped
- truth is never mutated by render/view downgrade

## 5) Proof And Replay Guarantees

Replay and proof surfaces are frozen with these baseline fingerprints:

- replay window fingerprint: `a92ae5ecb5aa156f2ebcac4bd4e9e2cc93584249cd4c0fce939be31022843572`
- replay window run hash: `5149ffd9e0340cdd20b802189a0a9cc2a82a11008c5cfbd7ed6ded0c80d91837`
- overlay identity fingerprint: `6eba60c59376594d858b2d8aafdb757dcdd07bf9b3e274a7c8a882fe26c1b6b0`
- overlay identity run hash: `ab16c693adf0ec58ebec32c6b6bc48e371a7cbaee9f8fff559117407585f3281`
- GEO reference suite fingerprint: `4e5891fcec7c014a58b14685eee0b76bcd33d8f5999961f44c6f88733d83d635`

The replay window verifies stable:

- cell key chains
- distance and metric hash surfaces
- field sample hashes
- overlay manifest and merge hash chains
- geometry state and edit hash chains
- worldgen result hash chains
- projected view fingerprints
- path result hash chains

Overlay identity verification confirms:

- canonical base IDs survive official, mod, and save layers
- new overlay-added objects are additive only
- property origin chains remain explainable

## 6) Regression Lock

The GEO regression lock is:

- `data/regression/geo_full_baseline.json`

Frozen baseline fingerprint:

- `b64f1e15940873bd919f0c7919d752d6b0d4e9b83d6808dd8d8e7486efe6b0ac`

Baseline updates require:

- commit tag `GEO-REGRESSION-UPDATE`
- rerun of stress, replay, overlay identity, and bounded GEO reference fixtures

## 7) Readiness Checklist

- GEO universes are portable across infinite, torus, atlas, portal-identified, and R4-stub spaces.
- Stable IDs survive overlays and replay windows.
- Geometry edits replay from compaction anchors without drift.
- Projection views remain lens-gated and truth-safe.
- Bounded reference evaluators cover small metric, neighborhood, and overlay fixtures.
- The full GEO subsystem is ready for MVP worldgen planning and long-horizon regression locking.
