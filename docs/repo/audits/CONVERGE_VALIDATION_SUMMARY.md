# CONVERGE Validation Summary

Status: PROVISIONAL

Phase: CONVERGE-12

Date: 2026-05-12

## Validator Commands

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root .` | pass | Audit mode exits zero. |
| `python tools/validators/check_repo_layout.py --repo-root . --json` | pass | JSON mode exits zero. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | Passes with active exceptions. |
| `python tools/validators/check_root_allowlist.py --repo-root .` | pass | Audit mode exits zero. |
| `python tools/validators/check_root_allowlist.py --repo-root . --json` | pass | JSON mode exits zero. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | Passes with active exceptions. |
| `python tools/validators/check_distribution_layout.py --repo-root .` | pass | Audit mode exits zero. |
| `python tools/validators/check_distribution_layout.py --repo-root . --json` | pass | JSON mode exits zero. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | Distribution strict passes. |
| `python tools/validators/check_component_matrices.py --repo-root .` | pass | Audit mode exits zero. |
| `python tools/validators/check_component_matrices.py --repo-root . --json` | pass | JSON mode exits zero. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | Component matrix strict passes. |

## Strict Validator Results

Strict validators pass.

Active layout exceptions: 37.

Unexcepted layout violations: 0.

All active exceptions now use `POST-CONVERGE` retirement metadata because CONVERGE-12 performed audit cleanup, not broad physical exception retirement.

## Supplemental Checks

| Command | Result | Notes |
| --- | --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK. |
| `python scripts/dev/gate.py verify --repo-root .` | fail | Existing xstack FAST `repox_runner` STRUCTURAL failure. |
| `cmake --preset verify` | fail | Visual Studio 17 2022 generator unavailable locally. |
| `cmake --build --preset verify` | not run | Configure failed. |
| `ctest --preset verify` | not run | Configure failed. |
| `git diff --check` | pass | CRLF conversion warnings only. |

## AIDE Checks

| Command | Result | Notes |
| --- | --- | --- |
| `python .aide/scripts/aide_lite.py doctor` | pass | AIDE Lite doctor passed. |
| `python .aide/scripts/aide_lite.py validate` | pass | AIDE Lite validate passed with existing warnings. |
| `python .aide/scripts/aide_lite.py pack --task "CONVERGE-12 final stale documentation and layout audit cleanup"` | fail | Local Python lacks `Path.write_text(newline=...)` support. |

## Readiness

The repo is ready for post-CONVERGE work with warnings:

- strict layout validators pass only because 37 active exceptions remain explicit
- the local CMake verify lane cannot configure without Visual Studio 17 2022
- the broader FAST gate still reports a structural `repox_runner` failure

These warnings are documented and do not indicate a CONVERGE-12 stale-doc cleanup failure.
