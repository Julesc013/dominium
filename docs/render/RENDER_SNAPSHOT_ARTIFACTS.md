Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Render Snapshot Artifacts

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: normative  
Version: 1.0.0  
Scope: RND-2 derived render capture pipeline

## Artifact Class

`RENDER_SNAPSHOT` artifacts are **DERIVED**.

They are generated from `RenderModel` and renderer policy, and do not alter simulation truth.

## Artifact Set

Baseline capture output:

1. `render_snapshot.json`
2. `frame_summary.json`
3. `frame_layers.json` (renderer summary breakdown)
4. optional image payload (`.ppm`/raw/png depending on renderer/tool options)

## Schema Contract

1. `schema/render/render_snapshot.schema`
2. `schema/render/frame_summary.schema`

`render_snapshot` links RenderModel identity and output references.
`frame_summary` is deterministic metadata used for regression checks.

## Storage Convention

Default deterministic storage root:

1. `run_meta/render_snapshots/<snapshot_id>/`

Allowed alternative deterministic path:

1. `out/render/<tick>/<viewpoint_id>/`

## Caching

Snapshot reuse key:

1. `(render_model_hash, renderer_id, width, height)`

Cache invalidation:

1. when `render_model_hash` changes
2. when renderer or resolution changes
3. when explicit cache-off flag is used

## Regression Usage

Recommended regression assertions:

1. summary schema validity
2. summary hash stability on identical input
3. optional same-platform pixel hash comparison
