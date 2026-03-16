Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MOB1 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-02
Scope: MOB-1 GuideGeometry rollout.

## 1) Existing spline/corridor and snapping logic

1. FORM inference already emits candidate geometry previews in `src/infrastructure/formalization/inference_engine.py`.
   - Candidate kinds currently: `spline`, `corridor`, `volume`, `graph_stub`.
   - These are derived-only and do not author canonical geometry rows.

2. Plan artifacts already carry spatial preview payloads in `src/control/planning/plan_engine.py`.
   - `plan_artifact.spatial_preview_data` stores deterministic ghost renderables/materials.
   - This is suitable for GuideGeometry planning previews.

3. There is no canonical mobility geometry state collection yet in authoritative runtime.
   - `tools/xstack/sessionx/process_runtime.py` currently has no `guide_geometries` or `mobility_junctions` state normalizers.

## 2) Coordinate frame assumptions and multi-scale risk

1. Existing spatial assumptions are mostly world-local integer millimeters (`position_mm`).
2. `process_runtime._target_spatial_position` resolves positions from entity rows and does not yet resolve geometry-owned spatial references.
3. `plan_engine` and inspection overlays render many previews with synthetic local transforms around origin.
   - Migration risk: if GuideGeometry parent `SpatialNode` frames are not explicit, cross-node overlays can drift semantically.

## 3) Existing special-case track geometry assumptions

1. `process.spec_check_compliance` in `tools/xstack/sessionx/process_runtime.py` has a `spec.track` branch.
   - It computes and auto-applies `effect.speed_cap` with `auto_spec_track_speed_cap` markers.
2. Derived compliance summaries are currently synthesized from generic inspection sections.
   - `derived.geometry.clearance_summary` and `derived.geometry.curvature_summary` are stubs unless explicit inputs exist.
3. No dedicated guide geometry metrics cache exists yet.

## 4) Migration plan to GuideGeometry substrate

1. Add canonical state collections:
   - `guide_geometries`
   - `mobility_junctions`
   - `geometry_candidates`
   - `geometry_derived_metrics`
2. Add deterministic geometry processes only:
   - `process.geometry_create`
   - `process.geometry_edit`
   - `process.geometry_finalize`
3. Bridge FORM acceptance:
   - `process.formalization_accept_candidate` must create formal guide geometry artifact rows.
4. Move mobility/spec checks to geometry-derived metrics:
   - curvature bands
   - clearance envelope stub
   - gauge stub values
5. Extend inspection overlays to render guide geometry centerlines/corridors/volumes/junction glyphs.
6. Add RepoX/AuditX checks to prevent geometry mutation bypass and hardcoded gauge assumptions.

## 5) Deprecation targets

- Inline track/rail special-casing for geometry compliance in process runtime.
- Any future direct mutation of geometry rows outside process execution.
- Any hardcoded guide/snap behavior that bypasses snap policy registries.
