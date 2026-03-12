Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Terrain Collision Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A3` Observer and truth remain separate
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/canon/constitution_v1.md` `E7` Cross-platform replay agreement
- `docs/embodiment/EMBODIMENT_BASELINE.md`
- `docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`

## 1) Purpose

EARTH-6 adds deterministic terrain grounding for embodied bodies in MVP v0.0.0.

The model exists to:

- keep capsule bodies in lawful ground contact over macro terrain
- apply deterministic slope response to movement
- remain compatible with future micro chunks and richer collision providers

It does not implement a rigid-body solver, mesh collision, or arbitrary contact manifolds.

## 2) Activation Surface

- The canonical provider interface is `collision_provider`.
- The MVP provider is `collision.macro_heightfield_default`.
- Mutation occurs only through:
  - `process.body_apply_input`
  - `process.body_tick`

No UI, renderer, or tool may commit terrain contact directly.

## 3) Terrain Height Query

Terrain height is queried deterministically from the active collision provider.

For the MVP macro heightfield provider:

1. resolve the active surface tile key from body/body-state context
2. resolve the effective tile height using:
   - GEO-7 geometry `height_proxy` if present
   - EARTH-1 hydrology-adjusted height proxy if present
   - base `elevation_params_ref.height_proxy` otherwise
3. optionally apply deterministic bilinear interpolation if the provider row enables the bilinear stub
4. otherwise use nearest-cell height

All sampling offsets, interpolation spans, and fallback rules are fixed by data.

## 4) Ground Contact Resolution

Each body capsule exposes:

- `radius_mm`
- `height_mm`
- `foot_offset_mm`

After momentum integration:

- query `terrain_height_mm = h(position_ref)`
- compute `ground_contact_height_mm = terrain_height_mm + foot_offset_mm`
- if `body_position.z < ground_contact_height_mm`
  - clamp `body_position.z` to `ground_contact_height_mm`
  - zero the vertical velocity component
  - mark `grounded = true`
- otherwise
  - preserve vertical motion
  - mark `grounded = false`

Restitution is zero in MVP.
Ground snap uses a fixed deterministic tolerance only.

## 5) Slope Estimation

Slope is estimated from four fixed local samples:

- east
- west
- north
- south

Rules:

- sample offsets are fixed by provider/model data
- neighbor enumeration order is GEO-key deterministic
- ties are broken by lower `geo_cell_key`

The macro gradient vector is:

- `grad_x = height_east - height_west`
- `grad_y = height_north - height_south`

The slope angle is an integer approximation derived from gradient magnitude only.
No floating trig is required in authoritative evaluation.

## 6) Movement Response

Slope response modifies the force applied by `process.body_apply_input`.

Rules:

- uphill motion reduces acceleration
- downhill motion may receive bounded assist
- downhill assist is capped by `downhill_speed_cap_factor`
- slide threshold is recorded as metadata only in EARTH-6
- no full sliding solver is active yet

All modifiers are deterministic and data-declared through `movement_slope_params`.

## 7) Provider Interface

The collision provider contract supports:

- `macro_heightfield`
- `micro_chunk_future`
- `mesh_future`

The MVP provider must return:

- sampled tile key
- terrain height
- slope gradient proxy
- slope angle proxy
- deterministic fingerprint

Provider selection is data-driven through registries, not hardcoded mode branches.

## 8) Geometry Edit Integration

Geometry edits that change height invalidate collision samples locally.

Rules:

- dirty tile keys come from edited geometry cell keys
- invalidation is bounded to the edited window
- no global terrain collision rebuild is required for local edits
- re-query after invalidation must produce the updated height deterministically

## 9) Observer Surface

EARTH-6 may expose derived debug data:

- terrain height under observer/body
- grounded state
- slope angle

These are derived view surfaces only.
They must not mutate truth and must remain profile gated.

## 10) Non-Goals

- no rigid body manifold solver
- no arbitrary mesh collision
- no jump or crouch logic
- no wall-clock smoothing
- no nondeterministic retries
