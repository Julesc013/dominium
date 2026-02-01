Status: CANONICAL
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
# SPEC: Language Baselines (Domino C89 / Dominium C++98)

This repository has two forever-baselines:

- **Domino (engine/core)**: ISO **C89/C90** only, forever.
- **Dominium (product layer)**: ISO **C++98** only, forever.

## Baseline visibility rule (public headers)

Any header shipped under `include/` is **baseline-visible** and must not rely on
newer language syntax or libraries.

- **C89-visible headers** (primarily `include/domino/**`) must remain valid C89
  and also compile when included from C++98 translation units.
- **C++98-visible headers** (primarily `include/dominium/**`) must remain valid
  C++98 and must not require C++11 or newer features.

## Modern features (allowed only behind non-baseline layers)

Newer standards/features are allowed only in optional, non-baseline layers
(e.g. platform backends, tools, or acceleration paths) and must never be
required for correctness, determinism, or ABI compatibility.

## Hard rejection: runtime language switching

The project does **not** support runtime switching like “compile as C89 vs C11”
or selecting language standards at runtime. Language level is a **build-time**
contract, and baseline headers must be compatible by construction.
