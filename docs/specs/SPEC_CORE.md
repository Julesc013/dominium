--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

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
# Domino Core Notes

## Types and ids
- Base integers live in `domino/core/types.h` (`u8/u16/u32/u64`, `i8/...`, `d_bool`).
- TLV wrapper: `d_tlv_blob { unsigned char *ptr; u32 len; }` for passing binary payloads around without owning the memory.
- Subsystem ids (`d_subsystem_id`) and model ids (`d_model_family_id`/`d_model_id`) reserve low ranges for engine use; mods expand from 1000+.

## Registry infrastructure
- Subsystems: `d_subsystem_register/lookup` backed by a fixed static table (deterministic, no heap churn).
- Models: `d_model_register/lookup` grouped by family with fixed per-family caps.
- Generic registries: `d_registry_init/add/get` use caller-provided storage to avoid hidden allocations; ids auto-increment from a caller-chosen base.
- TLV schemas: `d_tlv_schema_register/validate` keep validation/upgrade callbacks centralized and versioned.

## Architectural principles
- Fixed-timestep determinism; no platform-specific headers inside Domino code.
- Strict layering: platform (`dsys`), gfx (`dgfx`), sim/world, subsystems. Cross-subsystem behavior goes through public APIs and ids, never through internal struct peeking.
- Serialization goes through the subsystem registry + TLV containers so new systems can be added without touching the orchestrator.
