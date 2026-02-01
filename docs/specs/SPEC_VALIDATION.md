Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# SPEC_VALIDATION — Deterministic Validation Pipeline

This spec defines when validation runs, what it validates, and what it is
allowed to do. Validation is an engineering gate, not gameplay logic.

## Scope
Applies to:
- content validation after pack/mod load and before world creation
- subsystem validators after world creation/load and before simulation starts
- save verification via reload + world hash comparison

## Content validation (pre-world)
Content validation runs after all packs/mods are loaded into registries and
before any world instance is created.

Rules:
- It MUST be deterministic and independent of platform behaviors.
- It MUST validate referential integrity and schema constraints using stable
  IDs (no “best effort” fallback).
- It MUST NOT mutate authoritative world state (no world exists yet).

## Subsystem validation (post-world, pre-sim)
After a world is created or loaded, subsystem validators run before simulation.

Ordering:
- Validators MUST run in a deterministic order. The legacy orchestration uses
  the subsystem registry iteration order (`d_subsystem_get_by_index(i)`; see
  `docs/specs/SPEC_DOMINO_SUBSYSTEMS.md`).

Rules:
- Validators are pure reads of world state plus deterministic checks.
- Validators MUST NOT perform authoritative mutation as a “fixup”.
- Validators MUST NOT call OS APIs as validation inputs (time, filesystem
  enumeration, network).

## Save verification (world hash)
Save verification re-loads the freshly written world into a temporary instance
and compares **world hashes**:
- The comparison uses the authoritative world hash, not a build hash
  (`docs/specs/SPEC_DETERMINISM.md`).
- Any mismatch MUST be reported immediately; silent corruption is forbidden.

## Forbidden behaviors
- Skipping validation based on UI state, wall-clock time, or platform heuristics.
- Hashing/serializing raw memory blocks that include padding/pointers.
- Non-deterministic “auto repair” during validation.

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/specs/SPEC_DOMINO_SUBSYSTEMS.md`
- `docs/specs/SPEC_PACKETS.md`