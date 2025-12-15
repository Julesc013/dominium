# Dominium — Building (Authoritative)

This document defines the build contract for this repository: Domino (engine),
Dominium (products), and tests. It does not define engine behavior; simulation
and determinism rules are specified in `docs/SPEC_DETERMINISM.md`.

## Build system
- CMake is the canonical build system.
- Minimum CMake version: **3.16** (see root `CMakeLists.txt`).
- Builds MUST NOT fetch network dependencies. Vendored sources live under
  `external/`.

Recommended out-of-source build:
```
cmake -S . -B build
cmake --build build
```

## Language levels (build-enforced)
- C code is compiled as C90 (`CMAKE_C_STANDARD 90`, extensions off).
- C++ code is compiled as C++98 (`CMAKE_CXX_STANDARD 98`, extensions off).

The language policy for deterministic code lives in `docs/LANGUAGE_POLICY.md`.

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
- System backends are selected via cache variables such as `DSYS_BACKEND_*` and
  `DOMINO_USE_*_BACKEND` (see `source/domino/system/CMakeLists.txt`).

## Determinism build hygiene
Deterministic core code is guarded by test-time scans and must satisfy:
- no `float`/`double` tokens in deterministic core paths
- no `time()`/`clock()`/`<time.h>` usage in deterministic core paths
- no OS headers in deterministic core paths

See `docs/DETERMINISM_REGRESSION_RULES.md` and run the scan test:
```
ctest -R domino_det_regression_scan_test
```

## Build metadata (optional)
The repository contains a build-number helper script:
- State file: `.dominium_build_number`
- Generator: `scripts/update_build_number.cmake`

It can emit a generated header (e.g. under a build directory):
```
cmake -DSTATE_FILE=.dominium_build_number ^
      -DHEADER_FILE=build/generated/dom_build_version.h ^
      -DNUMBER_FILE=build/generated/build_number.txt ^
      -DPROJECT_SEMVER=0.1.0 ^
      -P scripts/update_build_number.cmake
```

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
