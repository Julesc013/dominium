# ARCH_BUILD_ENFORCEMENT — Build and Boundary Lockdown

Status: draft
Version: 1

## Purpose
This document describes the enforced build graph and architectural boundaries.
It defines what the build system and CI must reject to keep engine and game
separable and reusable.

## Target graph (authoritative)
```
domino_engine (engine/)
   ^
   |
dominium_game (game/)
   ^        ^
   |        |
 client   server

launcher (launcher/)  -> libs + schema + engine public API
setup    (setup/)     -> libs + schema
tools    (tools/)     -> libs + engine public API + schema
```

## Include boundaries (hard rules)
- `engine/include/**` is the ONLY public engine API surface.
- `engine/modules/**` and `engine/render/**` are engine-internal only.
- `game/` may include `domino/*` public headers only.
- `client/` and `server/` may include public engine/game headers only.
- `launcher/`, `setup/`, and `tools/` must never include engine internals.

## CMake enforcement
Enforcement is done via target-scoped includes and configure-time checks:
- `domino_engine` exposes only `engine/include/` publicly.
- `dominium_game` links against `domino_engine`; no engine internals are added.
- `client` and `server` link `domino_engine` + `dominium_game` only.
- Configure-time boundary checks in `CMakeLists.txt` fail if:
  - `domino_engine` links to game/launcher/setup/tools targets.
  - `dominium_game` links to launcher/setup targets.

## CI / static enforcement
The following checks must run in CI (and locally when possible):
- `scripts/verify_includes_sanity.py`
  - Fails if engine includes game/launcher/setup/tools headers.
  - Fails if game includes engine internals (`engine/modules/**`, `core/`, `sim/`, etc.).
  - Fails if client/server include engine or game internals.
- `scripts/verify_cmake_no_global_includes.py`
  - Fails if any `include_directories()` usage is detected.
- `scripts/verify_tree_sanity.bat`
  - Fails if engine tree contains launcher/setup/tools contaminants.

## Determinism smoke gates
Required CI baseline:
- Configure + build engine + game (headless).
- Run engine smoke tests via CTest.

## Common failure modes
- Including internal headers (e.g., `sim/`, `core/`, `modules/`) from game/client/server.
- Adding `include_directories()` in any CMake file.
- Linking `domino_engine` to game or launcher/setup targets.
- Linking `dominium_game` to launcher/setup targets.

## Local verification
Recommended commands:
```
scripts\verify_tree_sanity.bat
python scripts\verify_includes_sanity.py
python scripts\verify_cmake_no_global_includes.py
cmake --preset vs2026-x64-debug
cmake --build --preset vs2026-x64-debug
ctest --preset vs2026-x64-debug
```
