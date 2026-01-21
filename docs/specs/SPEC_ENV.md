--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_ENV — Environment (ENV)

This spec defines the deterministic environment subsystem (`D_SUBSYS_ENV`):
chunk-local zones/portals, coarse environmental fields, and an optional interior
volume graph used to apply deterministic overrides during sampling.

## Scope
Applies to:
- per-chunk ENV zones/portals (`denv_zone_state`, `denv_portal`)
- per-chunk field layers (`d_env_field_cell`)
- interior volume graph (`d_env_volume`, `d_env_volume_edge`)
- deterministic sampling (`d_env_sample_at`, `d_env_sample_exterior_at`)
- model dispatch (`d_env_model_vtable`) and ticking (`d_env_tick`)
- save/load framing under `TAG_SUBSYS_DENV`

Does not define UI, rendering, visibility, or any authoritative baked geometry.

## Owns / Produces / Consumes

### Owns (authoritative state)
Chunk-local:
- `denv_zone_state` arrays (zone id + scalar channels + optional `extra` TLV)
- `denv_portal` arrays connecting zones (area/permeability + optional `extra` TLV)

Chunk fields:
- `d_env_field_cell` arrays (field id + model id + `values[4]`)

Instance/global:
- `d_env_volume` and `d_env_volume_edge` graph (world-space AABB volumes with
  conductance edges)
  - volumes may be owned by a struct or vehicle entity id (`owner_struct_eid`,
    `owner_vehicle_eid`)

Authoritative invariants:
- All scalars are fixed-point (`q16_16`, `q32_32`).
- IDs are stable integers and MUST have a stable total order.
- Volume extents are parametric AABBs; ENV MUST NOT store baked meshes/triangles
  as truth.

### Produces (derived outputs)
- `d_env_sample` arrays returned by sampling functions.
- Optional acceleration structures for sampling/volume lookup; derived caches
  only.

### Consumes
- World coordinates and chunk partitioning.
- Model parameter blobs (`d_tlv_blob`) and model registry entries.

## Reserved field IDs (built-in atmosphere)
Built-in `d_env_field_id` values (`source/domino/env/d_env_field.h`):
- `D_ENV_FIELD_PRESSURE` (1)
- `D_ENV_FIELD_TEMPERATURE` (2)
- `D_ENV_FIELD_GAS0_FRACTION` (3)
- `D_ENV_FIELD_GAS1_FRACTION` (4)
- `D_ENV_FIELD_HUMIDITY` (5)
- `D_ENV_FIELD_WIND_X` (6)
- `D_ENV_FIELD_WIND_Y` (7)

Built-in model id:
- `D_ENV_MODEL_ATMOSPHERE_DEFAULT` (1)

## Determinism + ordering
- Sampling is deterministic and side-effect free:
  - the same `(world, tick, x,y,z)` yields the same samples and the same sample
    order
  - multi-sample returns MUST be in ascending `field_id` order
- Field sampling kernels MUST use explicit neighbor orders and fixed arithmetic
  weights (no tolerances/epsilons).
- Volume overrides:
  - `d_env_sample_at` may apply a matching interior volume override.
  - If multiple volumes contain the point, the selected volume MUST be the one
    with the lowest `d_env_volume_id` (stable tie-break).
- Budgeting:
  - Any integration into the refactor scheduler MUST express ENV work as bounded
    work items under deterministic budgets (`docs/SPEC_SIM_SCHEDULER.md`).
  - Legacy DSIM-era ticking may be unbudgeted, but MUST remain bounded by fixed
    table sizes and per-chunk caps.

## Persistence (save/load)
- Subsystem id: `D_SUBSYS_ENV` (`source/domino/core/d_subsystem.h`).
- Container tag: `TAG_SUBSYS_DENV` (`source/domino/core/d_serialize_tags.h`).
- Chunk payload includes zones/portals and field cells.
- Instance/global payload includes the volume graph (volumes + edges).

## Forbidden behaviors
- Floating-point, tolerance/epsilon comparisons, or adaptive kernels in
  deterministic paths.
- OS time, threads, filesystem/network IO as inputs to environment outcomes.
- Treating sample results or accelerators as authoritative truth.

## Source of truth vs derived cache
**Source of truth:**
- chunk zone/portal state
- chunk field cell values
- volume graph (volumes + edges)

**Derived cache:**
- sample outputs
- any sampling/lookup accelerators

## Note on “zones”
`denv_zone_state` is ENV’s chunk-local zone/portal representation. It is not
the same as the legacy `dzone` interior atmosphere registry in
`include/domino/dzone.h` (see `docs/SPEC_ZONES.md`).

## Implementation pointers
- `source/domino/env/d_env.h`, `source/domino/env/d_env_field.h`,
  `source/domino/env/d_env_volume.h`
- `source/domino/env/d_env.c`, `source/domino/env/d_env_volume.c`

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_DOMINO_SUBSYSTEMS.md`
- `docs/SPEC_SIM.md`
- `docs/SPEC_ZONES.md`
