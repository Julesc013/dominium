Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Dominium — Building (Authoritative)

This document defines the build contract for this repository: Domino (engine),
Dominium (products), and tests. Build topology is summarized in
`docs/guides/BUILD_OVERVIEW.md`.

## Build system
- CMake is the canonical build system.
- Minimum CMake version: **3.21** (root `CMakeLists.txt`).
- Builds are intended to be network-isolated by default; external code is
  vendored under `external/`, and `DOM_DISALLOW_DOWNLOADS` defaults to ON.

## Presets and configuration
- `CMakePresets.json` defines the canonical configure/build/test presets.
- Windows development uses the `vs2026-x64-debug` / `vs2026-x64-release` presets.
- Baseline and modern presets are documented in `docs/ci/BUILD_MATRIX.md`.

Example (Windows, VS 2026):
```
cmake --preset vs2026-x64-debug
cmake --build --preset vs2026-x64-debug
ctest --preset vs2026-x64-debug
```

## Language levels (build-enforced)
- C code is compiled as C90 (`CMAKE_C_STANDARD 90`, extensions off).
- C++ code is compiled as C++98 (`CMAKE_CXX_STANDARD 98`, extensions off).

## Toolchain policy (by host OS)
- Windows presets target MSVC (Visual Studio generator).
- Linux presets target GCC (Ninja generator).
- macOS presets target Xcode.
- MSYS2 presets exist but are marked legacy/hidden.

## Output locations
- Default outputs go to `${CMAKE_BINARY_DIR}/bin` and `${CMAKE_BINARY_DIR}/lib`.
- Some presets override output directories; see `CMakePresets.json`.
- Dist layout outputs are opt-in via `dist_set_role`; see
  `docs/guides/BUILD_DIST.md` and `docs/guides/build_output.md`.

## Component build toggles (root CMake)
- `DOM_BUILD_TESTS`, `DOM_BUILD_TOOLS`, `DOM_BUILD_SETUP`,
  `DOM_BUILD_LAUNCHER`, `DOM_BUILD_GAME`.

## Subsystem and tooling toggles
- `DOM_ENABLE_MODERN`, `DOM_ENABLE_AUDIO`, `DOM_ENABLE_NET`.
- `DOMUI_ENABLE_JSON_MIRROR`, `DOMUI_ENABLE_CODEGEN`.
- `SETUP_DEFAULT`, `SETUP_LEGACY_BUILD`, `SETUP_LEGACY_DEPRECATED_WARN`,
  `ENABLE_NSIS_DEV_INSTALLER`.
- `DOMINIUM_STATIC_GNU_RUNTIME` (MinGW/MSYS static runtime).

## Platform and renderer selection
- `DOM_PLATFORM` selects the system backend:
  `sdl2`, `win32`, `win32_headless`, `null`, `posix_headless`, `posix_x11`,
  `posix_wayland`, `cocoa`.
- `DOM_BACKEND_*` toggles select renderer backends:
  `SOFT`, `NULL`, `DX9`, `DX11`, `GL1`, `GL2`, `VK1`, `METAL`.
- `DOM_BACKEND_SDL2` controls the SDL2 platform backend; `DOM_PLATFORM=sdl2`
  forces it ON.
- `DOM_FETCH_SDL2` controls optional SDL2 fetch when downloads are allowed.
  `DOM_SDL2_ROOT` (or `SDL2_DIR`/`SDL2_PATH`) provides a local SDL2 install.
- `DOM_BACKEND_VECTOR2D` enables the optional vector acceleration layer.

## Packaging and dist controls
- `DOMINIUM_ENABLE_PACKAGING` enables packaging helper targets.
- `DOM_DISALLOW_DOWNLOADS` enforces no-download builds.
- `DOM_DIST_ROOT`, `DOM_DIST_OS`, `DOM_DIST_ARCH`, `DOM_DIST_VARIANT`
  configure dist routing.
- `DOM_DIST_SEED_RUNTIME`, `DOM_DIST_INSTALL_TYPE`, `DOM_DIST_BUILD_CHANNEL`
  control runtime seeding when available.

## Build metadata (required)
- State file: `.dominium_build_number`
- Generator: `setup/packages/scripts/update_build_number.cmake`
- Root CMake adds `dom_update_build_number` to `ALL` (refresh only).
- Gated bump targets: `dom_bump_build_number` or `testx_all` (after tests).

## Tests and checks
- `DOM_BUILD_TESTS=ON` enables engine tests (`engine/tests`) and game tests
  (`game/tests/phase6`).
- `DOM_BUILD_TOOLS=ON` enables `validate_all` fixture tests under
  `tools/validation/fixtures`.
- Root CMake registers `launcher_help` and `setup_help` CTest entries when
  those components are built.
- `check_arch` runs `tools/ci/arch_checks.py` for static architecture rules.

## Running tests
```
ctest --test-dir <builddir>
```