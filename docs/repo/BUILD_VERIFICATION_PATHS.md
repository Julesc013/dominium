# Build Verification Paths

## Status

- Phase: POST-CONVERGE-06
- Current status: partially proven

POST-CONVERGE-06 confirmed that repository layout and supplemental validators can run locally, but the canonical CMake verify lane is still blocked by this machine's missing Visual Studio toolchain.

## Canonical Verify Lane

The canonical lane remains:

```text
cmake --preset verify
cmake --build --preset verify
ctest --preset verify
```

`verify` inherits `verify-win-vs2026` and `msvc-base` in `CMakePresets.json`.

| Property | Value |
| --- | --- |
| Generator | `Visual Studio 17 2022` |
| Architecture | `x64` |
| Binary dir | `${sourceDir}/out/build/vs2026/${presetName}` |
| Build type | `Debug` |
| Tests | `DOM_BUILD_TESTS=ON` |
| Local status | blocked, no Visual Studio instance found |
| CI status | intended MSVC proof lane if CI has Visual Studio 2022 |

## Local Fallback Lane

No local fallback preset was added in POST-CONVERGE-06.

Reason:

- `where.exe cl`: not found
- `where.exe ninja`: not found
- `where.exe gcc`, `clang`, `clang-cl`, `mingw32-make`, `nmake`, and `make`: not found

Adding `verify-ninja` or `verify-local` without a discovered compiler would be speculative and unvalidated. A future fallback preset should be added only after a concrete local toolchain exists and its support tier is documented.

## Build/Test Commands

Canonical configure:

```text
cmake --preset verify
```

Canonical build, run only after configure passes:

```text
cmake --build --preset verify
```

Canonical tests, run only after configure and build pass:

```text
ctest --preset verify
```

## Environment Requirements

- CMake: local `cmake version 4.2.0` is available.
- Generator: `Visual Studio 17 2022` is required by the visible `verify` lane.
- Compiler/toolchain: Visual Studio 2022 Build Tools or equivalent VS instance must be installed.
- Python: local `Python 3.8.1` is present and sufficient after the AIDE writer compatibility fix.
- Host: current visible canonical lane is Windows/MSVC-oriented.

## Current Gaps

- Local Visual Studio 2022 generator instance is missing.
- Local configure/build/CTest proof is not complete.
- No validated fallback preset exists.
- FAST still fails after the structural fix because RepoX now exposes broad drift and missing-artifact backlog.
