Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH Terrain Collision Baseline

## Scope

This report records the EARTH-6 baseline for deterministic terrain grounding and slope-aware movement in Dominium v0.0.0.

## Collision Provider Interface

Implemented provider surface:

- canonical provider registry row `collision.macro_heightfield_default`
- provider kind `macro_heightfield`
- deterministic local height query from:
  - GEO-7 geometry `height_proxy` when present
  - EARTH-1 hydrology-adjusted height proxy when present
  - base EARTH-0 elevation proxy otherwise
- bounded four-sample slope probe with fixed offsets
- local cache invalidation keyed by affected tile cell keys

The MVP provider remains compatible with future micro-chunk and richer collision backends without changing body or terrain identity contracts.

## Ground Contact Rules

Implemented contact model:

- `process.body_tick` performs the authoritative terrain contact pass after momentum integration
- terrain height is queried deterministically from the active provider
- contact height is `terrain_height_mm + foot_offset_mm`
- when the body falls below contact height:
  - `transform_mm.z` is clamped to contact height
  - vertical velocity is zeroed
  - `grounded = true`
- otherwise the body stays airborne and `grounded = false`

All authoritative contact mutation remains inside deterministic process execution.

## Slope Response

Implemented movement response:

- `process.body_apply_input` queries the same collision provider for macro slope
- uphill intent reduces horizontal force by `uphill_slow_factor`
- downhill intent may receive bounded assist capped by `downhill_speed_cap_factor`
- slide threshold is recorded as deterministic metadata only in EARTH-6
- no sliding solver or rigid-body contact manifold is active

The current fixture exercises a west-to-east uphill/downhill neighborhood and yields stable uphill/downhill modifiers with replay-stable force application.

## Geometry Edit Integration

Implemented local invalidation:

- geometry edits that touch surface height invalidate cached collision samples for affected tile keys only
- local re-query observes updated height deterministically
- no global terrain collision rebuild is required for small edits

The EARTH-6 replay/probe fixture confirms a local geometry removal updates collision height from the pre-edit sample to the new sample without changing unrelated tiles.

## Debug And Observer Surfaces

Derived debug surfaces now expose, subject to profile gating:

- grounded state
- terrain height under the active body/selection
- ground-contact height
- slope angle proxy
- slope acceleration modifier

These are observer-facing artifacts only and do not mutate truth.

## Validation Snapshot

Validated in this task:

- EARTH-6 TestX subset:
  - `test_ground_clamp_deterministic`
  - `test_grounded_state_set_correctly`
  - `test_slope_modifier_changes_speed`
  - `test_geometry_edit_changes_height`
  - `test_cross_platform_collision_hash_match`
- replay tool:
  - `tools/embodiment/tool_replay_movement_window.py`
- RepoX invariants:
  - `INV-COLLISION-DETERMINISTIC`
  - `INV-NO-POSITION-WRITE-BYPASS`
- AuditX analyzers:
  - `E368_DIRECT_POSITION_WRITE_SMELL`
  - `E380_NONDETERMINISTIC_COLLISION_SMELL`

## Forward Readiness

EARTH-6 is ready for:

- EARTH-7 wind proxy coupling against grounded and slope-aware embodiment
- EARTH-8 water visuals against grounded coastal traversal
- later micro-chunk collision refinement without replacing the MVP grounding contract
