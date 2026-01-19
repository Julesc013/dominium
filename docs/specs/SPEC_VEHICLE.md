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
# Vehicles (VEH)

The vehicle subsystem stores vehicle instances and dispatches to registered vehicle models for motion/state updates. Vehicles can optionally contribute interior ENV volumes (cabins) using data-driven TLVs.

## 1. Instances
- `d_vehicle_instance` captures id, proto id, position/velocity, rotation, chunk id, flags, optional entity link, and an opaque TLV `state` blob.
- Chunk save/load under `TAG_SUBSYS_DVEH` writes count + instance records. Instance-level data is currently empty.

## 2. Models
- Vehicle models register under `D_MODEL_FAMILY_VEH` (`dveh_model_vtable`).
- Tick walks vehicles and dispatches `tick_vehicle` when present.

## 3. ENV Volume Integration
- Vehicle prototypes (`d_proto_vehicle.params`) may include an environmental volume graph:
  - `D_TLV_ENV_VOLUME`: local AABB in Q16.16 (min/max for x/y/z)
  - `D_TLV_ENV_EDGE`: connects local volumes (`A`,`B`), where `B=0` couples to exterior; includes `GAS_K` and `HEAT_K`
- Created volumes are added to the ENV volume graph with `owner_vehicle_eid = vehicle_instance_id` and removed on destroy.

