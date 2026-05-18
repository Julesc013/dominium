# POST-CONVERGE-06 Build / FAST / AIDE Remediation

## Status

- Task ID: POST-CONVERGE-06
- Result: partial
- Date/time: 2026-05-12T20:55:02+10:00
- Branch: `main`
- HEAD SHA: `b08080e478c131b489545e813767c3f3aedc3367`
- origin/main SHA: `44bf83626fd1efade2d8e96ffe5bf8497a5aed3b`
- Working tree status before task: clean; `main` was ahead of `origin/main` by 1 local POST-CONVERGE-05 commit
- Working tree status after task: POST-CONVERGE-06 deliverables modified and ready for commit; no unrelated working-tree changes observed

## Scope

This task covered:

- build/toolchain diagnostics
- FAST/XStack gate diagnostics and targeted remediation
- AIDE pack diagnostics and remediation
- no feature work
- no runtime proof
- no platform/render/native implementation
- no semantic changes

## Build Preset Inspection

| Preset | Generator | Binary Dir | Purpose | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `local` | `Visual Studio 17 2022` | `${sourceDir}/out/build/vs2026/${presetName}` | local Windows configure | blocked | no VS instance found locally |
| `verify` | `Visual Studio 17 2022` | `${sourceDir}/out/build/vs2026/${presetName}` | canonical verify configure | blocked | visible canonical lane |
| `release-check` | `Visual Studio 17 2022` | `${sourceDir}/out/build/vs2026/${presetName}` | release check configure | not run | same generator family |
| `release-winnt-x86_64` | `Visual Studio 17 2022` | `${sourceDir}/out/build/vs2026/${presetName}` | Windows release configure | not run | same generator family |

Hidden and advanced presets exist in `CMakePresets.json`, but no local compiler or build tool was discovered to validate a fallback preset.

## CMake Verify Result

Command:

```text
cmake --preset verify
```

Result:

- exit code: 1
- classification: `missing_generator`

Failure summary:

```text
Generator Visual Studio 17 2022 could not find any instance of Visual Studio.
```

Remediation:

- no preset change was made
- documented the canonical MSVC requirement in `docs/repo/BUILD_VERIFICATION_PATHS.md`
- no fallback preset was added because `cl`, `ninja`, `gcc`, `clang`, `clang-cl`, `mingw32-make`, `nmake`, and `make` were not available locally

## Build / CTest Result

| Command | Result | Not-run reason | Classification |
| --- | --- | --- | --- |
| `cmake --build --preset verify` | not run | configure failed | environment |
| `ctest --preset verify` | not run | configure failed | environment |

## FAST Gate Result

Command:

```text
python scripts/dev/gate.py verify --repo-root .
```

Initial result:

- exit code: 1
- failing runner: `repox_runner`
- classification: `stale_path_after_convergence`
- exact blocker: `ValueError: invalid mod policy registry`

Remediation taken:

- updated CompatX schema discovery to prefer `contracts/schema/`
- fixed worldgen source path references used by RepoX and the dynamic Earth surface generator import

Post-remediation result:

- exit code: 1
- primary failure class: `DRIFT`
- direct RepoX profile: 5 warnings, 1800 failures
- current state: original structural blocker fixed; remaining broad RepoX drift is not safe to remediate in this task

## AIDE Result

| Check | Result | Notes |
| --- | --- | --- |
| Python version | `Python 3.8.1` | `Path.write_text` has no `newline` parameter |
| doctor | pass | existing warnings only |
| validate | pass | existing review-packet warnings only |
| pack | pass | fixed shared writer compatibility |

Remediation:

- `.aide/scripts/aide_lite.py` now writes normalized text with `path.open("w", encoding="utf-8", newline="\n")`.

## Changes Made

- docs changed: added this audit plus build, FAST, and AIDE remediation docs
- CMake presets changed: no
- scripts changed: `scripts/ci/check_repox_rules.py`
- AIDE scripts changed: `.aide/scripts/aide_lite.py`
- gate config changed: no
- CompatX helper changed: `tools/xstack/compatx/schema_registry.py`
- worldgen path reference changed: `game/domain/worldgen/mw/mw_surface_refiner_l3.py`

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python -m py_compile .aide/scripts/aide_lite.py tools/xstack/compatx/schema_registry.py scripts/ci/check_repox_rules.py game/domain/worldgen/mw/mw_surface_refiner_l3.py` | pass | touched Python files parse |
| `python tools/validators/check_repo_layout.py --repo-root .` | pass | active exceptions: 32; unexcepted violations: 0 |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | generated local byproducts were removed before final strict run |
| `python tools/validators/check_root_allowlist.py --repo-root .` | pass | unexcepted violations: 0 |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | generated local byproducts were removed before final strict run |
| `python tools/validators/check_distribution_layout.py --repo-root .` | pass | warnings: 0 |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | strict result: pass |
| `python tools/validators/check_component_matrices.py --repo-root .` | pass | warnings: 0 |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | strict result: pass |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `cmake --preset verify` | fail | `missing_generator`: Visual Studio 17 2022 instance not found |
| `cmake --build --preset verify` | not run | configure failed |
| `ctest --preset verify` | not run | configure failed |
| `python scripts/dev/gate.py verify --repo-root .` | fail | primary failure class: `DRIFT`; old structural blocker no longer reproduces |
| `python .aide/scripts/aide_lite.py doctor` | pass | existing warnings only |
| `python .aide/scripts/aide_lite.py validate` | pass | existing review-packet warnings only |
| `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-06 build and gate remediation"` | pass | task packet unchanged after final rerun |
| `git diff --check` | pass | final whitespace check |
| `git diff --cached --check` | pass | final staged whitespace check |

## Remaining Blockers

- Build blocker: local Visual Studio 2022 generator instance is missing.
- FAST blocker: RepoX broad drift backlog remains after structural stale-path fixes.
- AIDE blocker: none known after remediation.
- Environment blocker: no local compiler/build tool was discoverable for fallback configure/build/CTest.
- Unknown blockers: compile/test status remains unknown until a valid generator/toolchain is installed or available in CI.

## Readiness For POST-CONVERGE-07

Status: `not_ready`

Reason:

- local configure/build/CTest proof is not complete
- FAST still fails, though the POST-CONVERGE-00 structural blocker is fixed and remaining drift is now explicit

POST-CONVERGE-07 should wait for either local MSVC toolchain installation plus build proof, or an explicit reviewed decision that CI/MSVC proof plus documented FAST drift is sufficient for runtime proof.
