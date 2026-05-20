Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: prior C89/C++98 mainline language baseline
Superseded By: none
Stability: provisional
Future Series: LANGUAGE-BASELINE, PORTABILITY-MATRIX
Replacement Target: none; `contracts/build/language_baseline.contract.toml` is the machine-readable mirror

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Owns deterministic substrate, public C-compatible ABI, fixed-point math,
  scheduling primitives, and reusable runtime-independent services.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Tools may consume public APIs if needed and may use Python or C17/C++17
  according to ownership.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.
- No C++ ABI, STL containers, exceptions, or RTTI across stable public C ABI.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC: Language Baselines (Dominium C17 / C++17)

This repository has one active mainline source baseline:

- **C code**: ISO **C17**, extensions off.
- **C++ code**: ISO **C++17**, extensions off.

## Baseline visibility rule (public headers)

Any header shipped under a public include root is **baseline-visible** and must
not leak implementation, platform, or C++ ABI details into stable public ABI.

- **C-visible headers** must remain C17 C-compatible and also compile when
  included from C++17 translation units.
- **C++-visible headers** may use C++17 only when the surface is explicitly
  C++-scoped and does not become a stable C ABI promise.

## C++17 library subset

C++17 language mode is the mainline floor, but macOS 10.9.5 requires a
restricted standard-library subset. Mainline code must not require
`std::filesystem`, `std::pmr`, `std::to_chars`, `std::from_chars`, `std::any`,
or unguarded throwing optional/variant access paths.

## Retired baseline

C89/C++98 is retired from active mainline law. It may remain in historical
archives or future retro research lanes, but it must not govern default
configure/build/test presets.

## Hard rejection: runtime language switching

The project does **not** support runtime language-standard switching. Language
level is a **build-time** contract, and baseline headers must be compatible by
construction.
