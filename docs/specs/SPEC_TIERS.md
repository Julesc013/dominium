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
# SPEC_TIERS — Performance Tier Profiles (Non-Sim)

This spec defines performance tier profiles used to scale derived work,
presentation cadence, and runtime budgets without affecting authoritative
simulation.

## 1. Scope
- Tiers are **non-sim**: they MUST NOT change authoritative state, commands,
  or determinism hashes.
- Tiers are negotiated via `PERF_CAPS` (see `docs/specs/SPEC_CAPABILITIES.md`).
- Tiers are not part of identity digests; they are advisory and adjustable.
- SIM_CAPS are separate and pinned; see `docs/specs/SPEC_CAPABILITIES.md`.

## 2. Tier IDs (stable)
Tier IDs are `u32` values:
- `0` = `BASELINE` (Win95-class target)
- `1` = `MODERN`
- `2` = `SERVER`

## 3. Intended use
Tier profiles may tune:
- derived job budgets and IO concurrency
- snapshot cadence and presentation frequency
- cache sizes and non-authoritative LOD detail

Tier profiles MUST NOT:
- alter canonical timebase or tick order
- alter fixed-point math or deterministic RNG
- change schema/feature compatibility rules

## 4. Defaults
If no tier is supplied, runtime defaults to `BASELINE`.

## Related specs
- `docs/specs/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/specs/SPEC_CAPABILITIES.md`
- `docs/specs/SPEC_QOS_ASSISTANCE.md`
- `docs/specs/SPEC_DETERMINISM.md`