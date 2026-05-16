# Build Verification Paths

## Status

- Phase: POST-CONVERGE-10F
- Current status: build proven, targeted AuditX fixed, unit invariant fixed, CTest blocked by RepoX and discovery/wall-time gates

POST-CONVERGE-06 confirmed that repository layout and supplemental validators can run locally, while the canonical CMake verify lane was blocked by this machine's missing Visual Studio toolchain at that time. POST-CONVERGE-07 confirmed that no local product runtime proof could proceed without build output or an accepted equivalent CI proof.

POST-CONVERGE-08 re-ran `cmake --preset verify` with the same missing-generator failure. Product boot proof is therefore limited to script/wrapper AppShell help surfaces and does not replace native configure/build/CTest proof.

POST-CONVERGE-10 added a tuple-driven build contract and local machine probe. POST-CONVERGE-10B reprobed after Visual Studio installation. POST-CONVERGE-10C fixed the stale client/server source paths in active CMake and test inputs. POST-CONVERGE-10D fixed the UI bind byte-for-byte freshness issue by pinning tracked UI bind generated sources to LF line endings. POST-CONVERGE-10E fixed the targeted AuditX path and generated-projection blockers. POST-CONVERGE-10F fixed the unit invariant blocker. The VS2022/MSVC v143 tuple and the canonical `verify` preset now configure and build successfully, focused AuditX CTest cases pass, and focused tuple `invariant_units_present` passes. Full CTest is still blocked by `inv_repox_rules`, canonical `verify` CTest discovery, and local wall-time.

Build contract references:

- `contracts/build/floors.toml`
- `contracts/build/toolchains.toml`
- `contracts/build/tuples.toml`
- `contracts/build/artifacts.toml`
- `docs/build/BUILD_CONTRACT.md`

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
| Local status | configure and build pass; focused AuditX and unit invariant tests pass in tuple lane; canonical CTest discovery currently reports 0 tests; full CTest remains blocked by RepoX and wall-time |
| CI status | intended MSVC proof lane if CI has Visual Studio 2022 |

## Local Fallback Lane

No committed fallback preset was added in POST-CONVERGE-06, POST-CONVERGE-10, or POST-CONVERGE-10B.

Reason:

- `where.exe cl`: not found, but CMake finds the VS2022-local compiler through the Visual Studio generator
- `where.exe ninja`: not found
- `where.exe gcc`, `clang`, `clang-cl`, `mingw32-make`, `nmake`, and `make`: not found

POST-CONVERGE-10B generated ignored local preset data at:

```text
.dominium.local/CMakeUserPresets.generated.json
CMakeUserPresets.json
```

`CMakeUserPresets.json` is ignored/local and exists only so CMake can consume generated tuple presets. Regenerate it before rerunning tuple commands, and remove it before final strict layout validation. The generated presets expose `tuple.verify.winnt10.x64.msvc143.mt.debug`, `tuple.verify.host.host.host_default.host.debug`, and `tuple.smoke.host.host.host_default.host.debug`.

## Build Contract Commands

Probe:

```text
python tools/build/probe_toolchains.py --repo-root . --out .dominium.local/toolchains.detected.json
```

Generate local preset data:

```text
python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out .dominium.local/CMakeUserPresets.generated.json
```

Validate build contracts:

```text
python tools/build/validate_build_contract.py --repo-root . --strict
```

Run a tuple after a generated mapping exists:

```text
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --dry-run
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --configure
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --build
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --test
```

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
- Generator: `Visual Studio 17 2022` is required by the visible `verify` lane and is now backed by an installed VS2022 instance.
- Compiler/toolchain: Visual Studio Enterprise 2022 with C++ tools is detected; CMake selected MSVC tools `14.44.35207`.
- Windows SDK: CMake selected `10.0.26100.0`.
- Python: local `Python 3.8.1` is present and sufficient after the AIDE writer compatibility fix.
- Host: current visible canonical lane is Windows/MSVC-oriented.

## Current Gaps

- Local Visual Studio 2022 generator instance is present.
- Stale client/server CMake and test paths were remediated in POST-CONVERGE-10C.
- UI bind generated-output freshness was remediated in POST-CONVERGE-10D.
- Tuple and canonical `verify` builds now pass.
- Local Visual Studio 2026 and 2017 instances are not detected.
- Local configure/build proof is complete for the VS2022/v143 tuple and canonical `verify` preset.
- CTest proof is not complete: focused AuditX tests pass, focused tuple `invariant_units_present` now passes, focused tuple `inv_repox_rules` still fails, canonical `ctest --preset verify -N` currently reports 0 tests, and prior full CTest exceeded the local 40-minute shell timeout.
- Native product binaries are produced locally by the tuple build; canonical `verify` produces setup/launcher/client/server binaries.
- FAST still fails after the structural fix because RepoX exposes broad drift and missing-artifact backlog; tuple CTest exposes the same broad RepoX blocker through `inv_repox_rules`.
- POST-CONVERGE-07 could not run product binaries or prove local playtest/session/status/save/load/resume.
- POST-CONVERGE-08 could not run native product binaries; only partial script/wrapper help surfaces were proven.
- The Python server AppShell script can be invoked, but direct script execution currently ignores CLI args, so it is not a canonical product command proof.
