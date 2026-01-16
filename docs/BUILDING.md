# Dominium — Building (Authoritative)

This document defines the build contract for this repository: Domino (engine),
Dominium (products), and tests. It does not define engine behavior; simulation
and determinism rules are specified in `docs/SPEC_DETERMINISM.md`.

## Build system
- CMake is the canonical build system.
- Minimum CMake version: **3.16** (see root `CMakeLists.txt`).
- Builds MUST NOT fetch network dependencies. Vendored sources live under
  `external/`.

Preferred preset builds (VS 2026):
```
cmake --preset vs2026-x64-debug
cmake --build --preset vs2026-x64-debug
ctest --preset vs2026-x64-debug
```

Recommended generic out-of-source build:
```
cmake -S . -B build
cmake --build build
```

## Language levels (build-enforced)
- C code is compiled as C90 (`CMAKE_C_STANDARD 90`, extensions off).
- C++ code is compiled as C++98 (`CMAKE_CXX_STANDARD 98`, extensions off).

The language policy for deterministic code lives in `docs/LANGUAGE_POLICY.md`.

## Toolchain policy (by host OS)
- Windows builds MUST use MSVC (Visual Studio generator).
- Linux builds MUST use GCC (`CMAKE_C_COMPILER=gcc`, `CMAKE_CXX_COMPILER=g++`).
- macOS builds MUST use the Xcode generator.

## Visual Studio 2026 (Open Folder)
1. Open the repository folder in Visual Studio.
2. Select the `vs2026-x64-debug` or `vs2026-x64-release` preset.
3. Build the default target (ALL) to compile engine, setup, launcher, and tools.

Preset build outputs land under `out/build/vs2026/<preset>/bin` and `out/build/vs2026/<preset>/lib`.

## Key build targets
- `engine::domino` (`engine_domino`): engine library.
- `setup_cli` (output `setup`): setup CLI (stubbed).
- `launcher_cli` (output `launcher`): launcher CLI (stubbed).
- `dominium-tools` (output `tools`): tools host (stubbed).
- `coredata_compile`, `coredata_validate`: coredata tooling (stubbed).
- `dominium_client` (output `client`), `dominium_server` (output `server`): game stubs.

## Important CMake options
Repository-wide options (root `CMakeLists.txt`):
- `DOM_BUILD_TESTS`: build CTest targets and smoke tests.
- `DOM_BUILD_TOOLS`: build tool targets.
- `DOM_BUILD_SETUP`: build setup targets.
- `DOM_BUILD_LAUNCHER`: build launcher targets.
- `DOM_BUILD_GAME`: build game/client/server targets.
- `DOMINIUM_STATIC_GNU_RUNTIME` (MinGW/MSYS): links libgcc/libstdc++ statically.
- `DOMINIUM_ENABLE_PACKAGING`: enables `scripts/packaging/**` helper targets.

Renderer backend toggles (`source/domino/render/CMakeLists.txt`):
- `DOMINO_GFX_ENABLE_VK1` (OFF by default) and legacy backend toggles such as
  `DOMINIUM_GFX_CGA`, `DOMINIUM_GFX_EGA`, `DOMINIUM_GFX_VGA`, `DOMINIUM_GFX_VESA`,
  `DOMINIUM_GFX_XGA`, etc.

System backend selection:
- System backends are selected via `DOM_PLATFORM` (e.g. `sdl2`, `win32`,
  `win32_headless`, `posix_x11`, `posix_wayland`, `cocoa`).
- `DOM_BACKEND_SDL2` is kept in sync when `DOM_PLATFORM=sdl2`.
- Windows presets prefer `sdl2` + `gl2`; if SDL2 is missing, configuration
  falls back to `win32` + `dx9` (see `CMakePresets.json`).
- Deprecated toggles (`DSYS_BACKEND_*`, `DOMINO_USE_*_BACKEND`) are not used.

## Determinism build hygiene
Deterministic core code is guarded by test-time scans and must satisfy:
- no `float`/`double` tokens in deterministic core paths
- no `time()`/`clock()`/`<time.h>` usage in deterministic core paths
- no OS headers in deterministic core paths

See `docs/DETERMINISM_REGRESSION_RULES.md` and run the scan test:
```
ctest -R domino_det_regression_scan_test
```

## Build metadata (required)
The repository uses a unified build-number system driven by CMake:
- State file: `.dominium_build_number`
- Generator: `setup/packages/scripts/update_build_number.cmake`

The root CMake adds `dom_update_build_number` to `ALL`, so every build produces
the generated header and build number artifacts automatically. Do not bypass it.

## Running tests
After configuring/building, run:
```
ctest --test-dir build
```

Smoke tests wired into CTest include:
- `engine_smoke`
- `launcher_help`
- `setup_help`

For VS 2026 presets:
```
ctest --preset vs2026-x64-debug
```

## Codex workflow
- Prefer presets (`vs2026-x64-debug` / `vs2026-x64-release`) so CMake stays aligned with VS.
- Use `CMAKE_EXPORT_COMPILE_COMMANDS=ON` output at `out/build/vs2026/<preset>/compile_commands.json` for clangd/Codex tooling.
