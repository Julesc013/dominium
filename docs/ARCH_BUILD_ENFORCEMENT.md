# ARCH_BUILD_ENFORCEMENT — Build and Boundary Lockdown (ENF1)

Status: enforced
Version: 2

## Purpose
This document defines the enforced build graph and architectural boundaries.
All violations MUST fail at configure or build time and MUST be treated as merge-blocking.

## Target graph (authoritative)
```
domino_engine (engine/)
   ^
   |
dominium_game (game/)
   ^        ^
   |        |
client   server

tools (tools/)   -> domino_engine + dominium_game only
launcher (launcher/) -> libs + schema only
setup (setup/)       -> libs + schema only

libs (libs/)   -> leaf libraries (no engine/game dependency)
schema (schema/) -> data contracts (no engine/game dependency)
```

## Include boundaries (hard rules)
- `engine/include/**` is the ONLY public engine API surface.
- `engine/modules/**` and `engine/render/**` are internal and FORBIDDEN outside `engine/`.
- `game/` MUST NOT include from `engine/modules/**` (ARCH-INC-001).
- `client/`, `server/`, `tools/` MUST NOT include from `engine/modules/**` (ARCH-INC-002).
- Public headers MUST live only under `engine/include/**` (ARCH-INC-003).
- No `include_directories()` usage is allowed anywhere (enforced by `scripts/verify_cmake_no_global_includes.py`).

## CMake enforcement (configure/build failures)
Enforcement is done via target-scoped includes and configure-time assertions:
- `domino_engine` exposes only `engine/include/` as PUBLIC include directories.
- `dominium_game` links only `domino_engine` and MUST NOT link launcher/setup/libs targets.
- `dominium_client` and `dominium_server` link only `domino_engine` + `dominium_game`.
- Configure-time boundary checks fail if:
  - `domino_engine` exposes any public include outside `engine/include/` (ARCH-INC-003).
  - `domino_engine` links to forbidden top-level targets (ARCH-DEP-001).
  - `dominium_game` links to launcher/setup/libs targets (ARCH-DEP-002).

## How violations fail
- **Configure-time**: target graph assertions and include boundary checks (ARCH-DEP-001..006, ARCH-INC-003).
- **Build-time**: illegal includes fail compilation due to missing include paths (ARCH-INC-001, ARCH-INC-002).
- **Static checks**: `scripts/verify_includes_sanity.py` validates include boundaries by path.

## Common errors and fixes
- **Error**: include of `engine/modules/**` from game/client/server/tools fails.
  - **Fix**: move the include to a public header under `engine/include/**` or use the public API.
- **Error**: `domino_engine` exposes non-public include directories.
  - **Fix**: remove public include paths and keep internal paths PRIVATE.
- **Error**: `dominium_game` links to launcher/setup/libs targets.
  - **Fix**: remove the dependency and route through `domino_engine` public interfaces.
- **Error**: `include_directories()` used in any CMake file.
  - **Fix**: replace with `target_include_directories()` on specific targets.

## Local verification (recommended)
```
python scripts/verify_includes_sanity.py
python scripts/verify_cmake_no_global_includes.py
cmake --preset vs2026-x64-debug
cmake --build --preset vs2026-x64-debug
ctest --preset vs2026-x64-debug
```
