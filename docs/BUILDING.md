# Dominium — Building (Authoritative)

This document defines the build contract for this repository: Domino (engine),
Dominium (products), and tests. It does not define engine behavior; simulation
and determinism rules are specified in `docs/SPEC_DETERMINISM.md`.

## Build system
- CMake is the canonical build system.
- Minimum CMake version: **3.16** (see root `CMakeLists.txt`).
- Builds MUST NOT fetch network dependencies. Vendored sources live under
  `external/`.

Preferred preset builds:
```
cmake --preset msvc-debug
cmake --build --preset msvc-debug
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

## Key build targets
- `domino_core` (static library): the engine implementation, including the
  deterministic core subsystems.
- `domino_sys` (static library): platform/system layer (dsys backends).
- Dominium products under `source/dominium/` (game, launcher, setup, tools).
- Tests are defined under `source/tests/` (ctest) and `tests/` (additional
  harnesses and fixtures).

## Important CMake options
Repository-wide options (root `CMakeLists.txt`):
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
- Generator: `scripts/update_build_number.cmake`

The root CMake adds `dom_update_build_number` to `ALL`, so every build produces
the generated header and build number artifacts automatically. Do not bypass it.

## Running tests
After configuring/building, run:
```
ctest --test-dir build
```

Useful deterministic tests include:
- `domino_det_regression_scan_test`
- `domino_pkt_determinism_test`
- `domino_sched_determinism_test`
- `domino_pose_anchor_quant_test`

## Inspecting backend selection
`dominium_game` and `dominium-launcher` can print the compiled backend set and
the deterministic selection result:
```
dominium_game.exe --profile=baseline --print-caps
dominium_game.exe --profile=compat --lockstep-strict=1 --print-selection
```
