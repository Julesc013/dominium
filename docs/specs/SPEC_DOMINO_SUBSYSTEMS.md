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
# SPEC_DOMINO_SUBSYSTEMS — Subsystem Registry + Serialization

This spec defines the deterministic subsystem registry used by the legacy DSIM
loop and by world save/load orchestration. It exists to keep lifecycle hooks
discoverable and deterministic.

## Scope
Applies to:
- `d_subsystem_desc` registry API (`source/domino/core/d_subsystem.h`)
- deterministic iteration order of registered subsystems
- save/load TLV container framing for per-subsystem payloads
- subsystem tag mapping (`source/domino/core/d_serialize_tags.h`)

Does not define the refactor SIM scheduler phases and delta-commit semantics
(`docs/SPEC_SIM_SCHEDULER.md`).

## Descriptor (`d_subsystem_desc`)
File: `source/domino/core/d_subsystem.h`

Fields:
- `subsystem_id` (`u16`): stable id; engine-reserved range starts at 1; mods use
  1000+.
- `name`: short label (`"world"`, `"env"`, …).
- `version` (`u32`): subsystem schema/ABI guard.
- `register_models()`: optional global init hook to populate model registries.
- `load_protos(blob)`: optional content/proto ingest hook (TLV-packaged).
- `init_instance(world)`: optional per-world initialization after create/load.
- `tick(world, ticks)`: deterministic fixed-step hook.
- `save_chunk/load_chunk`: chunk-level serializers.
- `save_instance/load_instance`: instance/global serializers.

## Registry ordering (authoritative)
- Registration happens at startup; duplicate ids are rejected.
- The registry is a fixed-size table (`source/domino/core/d_subsystem.c`).
- Iteration order is the registry index order:
  - DSIM subsystem ticks run in this order (`docs/SPEC_SIM.md`).
  - Save/load orchestration iterates in this order.

Subsystem callbacks MUST NOT depend on:
- pointer identity
- hash-table iteration order
- filesystem enumeration order
- OS time or platform scheduling

## Save/load container framing (TLV)
Implementation: `source/domino/world/d_serialize.h`, `source/domino/world/d_serialize.c`

Rules:
- Each subsystem payload is wrapped as a TLV record:
  - `tag` (`u32`): `TAG_SUBSYS_*` tag for the subsystem
  - `len` (`u32`): payload length in bytes
  - `payload` bytes: subsystem-defined blob
- Tag values live in `source/domino/core/d_serialize_tags.h`.
- Unknown `TAG_SUBSYS_*` tags are skipped deterministically during load.

Deterministic IO rule:
- Subsystem payloads MUST define explicit endianness/field widths and MUST NOT
  serialize raw C structs as blobs; see `docs/SPEC_DETERMINISM.md`.

## Forbidden behaviors
- Save callbacks mutating authoritative world state.
- Load callbacks using OS time, filesystem enumeration, or any nondeterministic
  source as input to authoritative state.

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_SIM.md`
- `docs/SPEC_VALIDATION.md`
