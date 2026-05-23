# FULL-GATE-LEGACY-TEST-ROUTE-01

Status: PASS_WITH_WARNINGS
Baseline Commit: 425ae2bab8ea19d7934c0fd36a783aadc8543142
Branch: main
Task Class: validation_audit
Date: 2026-05-24

## Purpose

Route or retire active full-gate test expectations that still required retired
pre-canon roots, without reopening broad directory cleanup and without
weakening the canonical structure hard gate.

## Required Context Inspected

- `git status`
- recent `git log`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PRESENTATION_CONTRACT_01.md`
- `docs/repo/audits/CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01.md`
- `contracts/testing/test_tiers.contract.toml`
- CTest registration under `CMakeLists.txt` and `tests/**/CMakeLists.txt`
- affected TestX/CTest Python tests under `tests/`
- canonical structure validators under `tools/validators/repo/`

## Stale Paths Found And Routed

| Retired expectation | Active failing surface | Canonical route |
| --- | --- | --- |
| `docs/ci/CI_ENFORCEMENT_MATRIX.md` | `phase6_audit` | `docs/testing/ci/CI_ENFORCEMENT_MATRIX.md` |
| `contracts/schemas/capability_baseline.schema` | `baseline_sku_contracts` | `contracts/schema/capability_baseline.schema` |
| `tools/modpack/modpack_cli.py` | `modpack_workspace_contracts` | `tools/package/modpack/modpack_cli.py` |
| `tools/workspace/workspace_cli.py` | `modpack_workspace_contracts` | `tools/repo/workspace/workspace_cli.py` |
| `data/profiles` | distribution profile tests | `content/profiles` |
| `tools/distribution/compat_dry_run.py` | `distribution_legacy_platform_profiles` | `tools/package/distribution/compat_dry_run.py` |
| `docs/app`, `docs/platform`, `docs/render`, `docs/repox` | `integration_meta` | `docs/apps`, `docs/runtime/platform`, `docs/runtime/render`, `docs/repo/repox` |
| `runtime/app/app_runtime.c` | `integration_meta` | `runtime/shell/lifecycle/app_runtime.c` |
| `game/rules/fab/fab_interpreters.cpp` | `const_determinism_hardlocks` | `game/domain/fabrication/fab_interpreters.cpp` |
| `contracts/schemas/*.schema` | `const_srz_contracts` | `contracts/schema/*.schema` |
| `libs/appcore/command/command_registry.c` | `capability_gating_contracts` | `runtime/shell/command/command_registry.c` |

## Classification Summary

| Class | Disposition |
| --- | --- |
| `active_full_gate_failure` | Routed to canonical paths in affected tests and validators. |
| `active_fixture_needs_update` | Updated CTest/TestX Python checks in place; no product paths moved. |
| `active_validator_failure` | Added `check_full_gate_legacy_paths.py` to prevent these full-gate regressions. |
| `historical_doc_ok` | Historical audit and migration mentions were left unchanged. |
| `generated_stale_report` | Stale AuditX/report references remain evidence-only and do not define active source truth. |
| `real_regression` | Canonical structure validators still reject retired active roots. |
| `compatibility_reference` | Compatibility shim metadata containing legacy path names was preserved. |

## Files Changed

- `.aide/reports/latest-warning-disposition.md`
- `.aide/reports/FULL-GATE-LEGACY-TEST-ROUTE-01-repox-profile.json`
- `.aide/reports/FULL-GATE-LEGACY-TEST-ROUTE-01-repox-proof-manifest.json`
- `docs/repo/audits/FULL_GATE_LEGACY_TEST_ROUTE_01.md`
- `tests/apps/baseline_sku_tests.py`
- `tests/apps/modpack_workspace_tests.py`
- `tests/contract/capability_gating_contracts.py`
- `tests/contract/determinism_hardlock_tests.py`
- `tests/contract/srz_contract_tests.py`
- `tests/distribution/distribution_legacy_platform_profiles_tests.py`
- `tests/distribution/distribution_sdk_profile_tests.py`
- `tests/integration/integration_meta_test.py`
- `tools/validators/ci/phase6_audit_checks.py`
- `tools/validators/repo/check_full_gate_legacy_paths.py`

## Validation

| Command | Result |
| --- | --- |
| `python tools/validators/repo/check_full_gate_legacy_paths.py --repo-root . --strict` | PASS |
| `ctest --preset verify -R "^(phase6_audit\|integration_meta\|const_determinism_hardlocks\|const_srz_contracts\|capability_gating_contracts\|baseline_sku_contracts\|modpack_workspace_contracts\|distribution_legacy_platform_profiles\|distribution_sdk_profile_contracts)$" --output-on-failure --timeout 300` | PASS, 9/9 |
| `python -m py_compile ...` for touched Python files | PASS |
| `python tools/validators/repo/check_canonical_structure.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict` | PASS |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS |
| `python tools/validators/testing/check_test_tiers.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict` | PASS_WITH_WARNINGS, 0 violations and 69 pre-existing dependency warnings |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...` | PASS_WITH_WARNINGS, stale AuditX output warning preserved |
| `git diff --check` | PASS |

## Structure Gate Preservation

The canonical structure hard gate was not weakened. Retired-root references
inside structure validators remain negative enforcement or compatibility
metadata. Old active roots such as `game/rules`, `contracts/schemas`,
`data/profiles`, and `libs/appcore` were not recreated.

## Remaining Full-Gate Debt

Full CTest was not claimed green by this task. Remaining full-gate failures, if
any, are outside the stale-root routing subset and must be handled by targeted
follow-up tasks rather than by recreating retired roots.

## Non-Goals Preserved

- No active source directories were moved.
- No product, runtime, renderer, native GUI, provider, package, module-loader,
  Workbench, gameplay, or release behavior was implemented.
- Presentation contracts were not broadened.
- Canonical structure validators were not relaxed.
- Queue/current and latest task packet were not updated because this was run as
  a parallel maintenance lane.

## Readiness Verdict

Feature readiness remains LIMITED. This task removes known stale full-gate path
expectations from the affected tests, but does not promote broad feature work or
claim full CTest success.

## Next Recommendations

- Mainline: `PROJECTION-CONFORMANCE-01`
- Maintenance: run a later full CTest audit to classify any non-path T4
  failures after this stale-root subset has been routed.
