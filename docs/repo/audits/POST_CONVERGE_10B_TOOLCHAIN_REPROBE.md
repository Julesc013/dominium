# POST-CONVERGE-10B Toolchain Reprobe and Native Build Attempt

## Status

- Task ID: POST-CONVERGE-10B
- Result: partial
- Date/time: 2026-05-13T17:08:59+10:00
- Branch: `main`
- HEAD SHA: `40b71c11a9ffb5e88719bbb557d48fc73980915f`
- origin/main SHA: `40b71c11a9ffb5e88719bbb557d48fc73980915f`
- Working tree status before task: clean; `main` synced to `origin/main`
- Working tree status after task: POST-CONVERGE-10B audit and proof docs modified for commit

## Scope

This task covered:

- toolchain reprobe
- generated local presets
- configure/build/test attempt
- native binary proof if possible
- no feature work
- no runtime proof
- no package proof
- no platform/render/native implementation

## User-Reported Machine Change

The user reported that this Windows 10 machine now has:

- Visual Studio 2022 Enterprise installed
- Visual Studio 2015 Enterprise installed

Other partitions and machines were treated as future machine profiles only. They were not probed or proven in this task.

## Probe Result

| Tool | Detected? | Version/Detail | Evidence | Notes |
| --- | --- | --- | --- | --- |
| CMake | yes | `4.2.0` | `cmake --version` | CMake lists `Visual Studio 17 2022` as the default generator on this host |
| Python | yes | `3.8.1` | `python --version` | build tooling runtime |
| VS2022 | yes | Visual Studio Enterprise 2022 `17.14.37301.10` | `vswhere -all -products * -format json` | installed, complete, launchable |
| MSVC v143 | yes | MSVC toolset selected as `14.44.35207`; compiler reports MSVC `19.44.35227.0` | CMake configure output | canonical tuple can be attempted |
| Windows SDK | yes | `10.0.26100.0` selected | CMake configure output and Windows Kits include directory | target host OS: Windows 10.0.19045 |
| VS2015 | yes | legacy Visual Studio 14.0 paths present | direct path probe under `C:\Program Files (x86)\Microsoft Visual Studio 14.0` | not used as first proof lane |
| MSVC v140 | present by path only | `VC\bin\cl.exe` exists | direct path probe | no POST-CONVERGE-10B tuple uses v140 |
| VS2026 | no | no installed instance | probe notes | generator name alone is not proof |
| Ninja | no | not found on PATH | `where.exe ninja` | not needed for VS generator |
| GCC | no | not found on PATH | probe | blocked |
| Clang | no | not found on PATH | probe | blocked |
| MSBuild | not on PATH | CMake can still drive the VS generator | `where.exe msbuild` not found | VS generator discovery is sufficient for configure attempt |
| `cl` | not on PATH | CMake finds VS-local compiler | `where.exe cl` not found; CMake compiler path found | Developer Prompt is not required for the VS generator path |

## Probe Tool Changes

No build tool scripts were changed. The existing probe detected `msvc143`, and direct `vswhere` checks confirmed the C++ tools requirement.

## Generated Presets

| Tuple | Generated? | Preset Name | Reason / Blocker |
| --- | --- | --- | --- |
| `verify.winnt10.x64.msvc143.mt.debug` | yes | `tuple.verify.winnt10.x64.msvc143.mt.debug` | VS2022 / MSVC v143 detected |
| `verify.host.host.host_default.host.debug` | yes | `tuple.verify.host.host.host_default.host.debug` | host default maps to detected VS generator |
| `smoke.host.host.host_default.host.debug` | yes | `tuple.smoke.host.host.host_default.host.debug` | host default maps to detected VS generator |
| `verify.winnt10.x64.msvc145.mt.debug` | no | none | VS2026 instance not detected |
| `research.xp.x86.msvc141_xp.mt.release` | no | none | VS2017 XP toolset not detected |
| `verify.linux.x64.gcc.host.debug` | no | none | GCC/build tool not detected |
| `verify.linux.x64.clang.host.debug` | no | none | Clang/build tool not detected |

Generated local files:

- `.dominium.local/toolchains.detected.json`
- `.dominium.local/CMakeUserPresets.generated.json`
- `CMakeUserPresets.json` was generated temporarily so CMake could consume the tuple presets, then removed before final strict layout validation

These files are ignored local machine surfaces and were not committed.

## Configure / Build / Test Result

| Tuple | Configure | Build | Test | Output Dir | Notes |
| --- | --- | --- | --- | --- | --- |
| `verify.winnt10.x64.msvc143.mt.debug` | fail during CMake generate | not run | not run | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug` | toolchain and SDK selected; generation fails on stale source paths |
| `verify` | fail during CMake generate | not run | not run | `out/build/vs2026/verify` | direct canonical preset now reaches the same source path blocker |

Failure classification: `path_stale_after_convergence`.

Primary CMake errors:

- `engine/tests/CMakeLists.txt` references `client/presentation/frame_graph_builder.cpp`; the tracked source now exists at `apps/client/presentation/frame_graph_builder.cpp`.
- `tests/authority`, `tests/tourist`, `tests/services`, and `tests/piracy_containment` reference `server/authority/dom_server_authority.cpp`; the tracked source now exists at `apps/server/authority/dom_server_authority.cpp`.

## Native Binary Result

| Product | Expected Binary | Produced? | Path | Notes |
| --- | --- | --- | --- | --- |
| setup | `setup` | no | none | configure did not generate build files |
| launcher | `launcher` | no | none | configure did not generate build files |
| client | `client` | no | none | configure did not generate build files |
| server | `server` | no | none | configure did not generate build files |
| tools | `tools` | no | none | configure did not generate build files |

Only CMake compiler-identification binaries were produced under generated build directories. No product binaries were produced.

## Blockers

- CMake test targets still reference pre-convergence root paths:
  - `client/presentation/frame_graph_builder.cpp`
  - `server/authority/dom_server_authority.cpp`
- Configure/build/test proof cannot proceed until those build/test references are remediated.
- Native product binaries remain missing.

## Files Added/Changed

- Added `docs/repo/audits/POST_CONVERGE_10B_TOOLCHAIN_REPROBE.md`.
- Updated `docs/repo/audits/POST_CONVERGE_10_BUILD_BINARY_PROOF.md`.
- Updated `docs/build/TOOLCHAIN_PROOF.md`.
- Updated `docs/repo/BUILD_VERIFICATION_PATHS.md`.
- Updated `docs/repo/BUILD_ENVIRONMENT_REMEDIATION.md`.
- Updated `docs/release/NATIVE_BINARY_PROOF.md`.
- Updated `docs/repo/POST_CONVERGE_NEXT_STEPS.md`.

No build scripts, CMake files, contracts, product source, runtime source, or package source were changed.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python .aide/scripts/aide_lite.py doctor` | pass | warnings only for existing optional AIDE artifacts |
| `python .aide/scripts/aide_lite.py validate` | pass | existing review packet warnings |
| `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-10B toolchain reprobe and native build attempt"` | pass | updated tracked task packet |
| `python tools/build/probe_toolchains.py --repo-root . --json` | pass | available: `host_default`, `msvc143` |
| `python tools/build/probe_toolchains.py --repo-root . --out .dominium.local/toolchains.detected.json` | pass | ignored local probe output written |
| `vswhere -all -products * -format json` | pass | VS2022 Enterprise detected |
| `vswhere -all -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json` | pass | VS2022 C++ tools detected |
| `python tools/build/validate_build_contract.py --repo-root . --strict` | pass | build contract valid |
| `python tools/build/generate_user_presets.py --repo-root . --dry-run` | pass | no probe supplied, all tuples blocked |
| `python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out .dominium.local/CMakeUserPresets.generated.json` | pass | generated 3 tuple presets |
| `python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out CMakeUserPresets.json --force` | pass | generated ignored CMake user presets for CMake consumption |
| `cmake --list-presets` | pass | generated tuple presets visible |
| `cmake --list-presets=all` | pass | generated configure/build/test presets visible |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --dry-run` | pass | printed configure/build/test commands |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --configure` | fail | tuple runner returned code 1 |
| `cmake --preset tuple.verify.winnt10.x64.msvc143.mt.debug` | fail | stale CMake source paths after toolchain selection |
| `cmake --preset verify` | fail | same stale CMake source paths |
| `cmake --build --preset verify` | not run | configure failed |
| `ctest --preset verify` | not run | configure failed |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | unexcepted violations: none |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | unexcepted violations: none |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | warnings: none |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | warnings: none |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK; shell emitted an unrelated oh-my-posh transient access message after command success |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `python tools/validators/check_local_playtest_path.py --repo-root .` | pass, blocked proof | product binaries still missing |
| `python tools/validators/check_product_boot_matrix.py --repo-root .` | pass, partial proof | product binaries still missing |
| `python tools/validators/check_portable_projection.py --repo-root .` | pass, partial proof | product binaries and projection root still missing |

## Readiness

- ready_for_POST_CONVERGE_11: no
- reason: no product binaries were produced; configure is now blocked by stale CMake/test source paths rather than missing Visual Studio.
