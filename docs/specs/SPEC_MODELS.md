Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

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
# Domino Model Registry

Models are small, typed behavior/config records (RES, ENV, BUILD, TRANS, VEH, JOB, NET, REPLAY). The core registry exposes a uniform way to register and enumerate them without subsystem-specific plumbing.

## d_model_desc
- `family_id` (`u16`): model family (RES/ENV/BUILD/etc.; mods use 1000+ later).
- `model_id` (`u16`): stable id within the family.
- `name`: human-friendly identifier.
- `version` (`u32`): per-model ABI/schema guard.
- `fn_table`: opaque pointer to a family-specific vtable (casted by the subsystem).

## API
- Register: `d_model_register(&desc)` (duplicate family+id rejected; fixed-capacity tables).
- Enumerate: `d_model_count(family)`, `d_model_get_by_index(family, idx)`.
- Lookup: `d_model_get(family, model_id)`.

## Intended usage
- Each subsystem defines its own vtable struct (e.g., `dres_model_vtable`) and passes its address via `fn_table`.
- Callers pick the model by `(family_id, model_id)` or iterate by family for discovery.
- Core does not interpret `fn_table`; subsystems own the meaning and lifetime.

## Extensibility goal
- Adding new resource/env/build/transport/vehicle/job/net/replay models does not touch core code.
- Mods and tools can register additional families and models while staying within the deterministic, fixed-capacity registry.