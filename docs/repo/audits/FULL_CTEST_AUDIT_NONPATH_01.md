Status: DERIVED
Last Reviewed: 2026-05-24
Supersedes: none
Superseded By: none
Result: PARTIAL
Task: FULL-CTEST-AUDIT-NONPATH-01
Branch: main
Starting commit: 3243fab7d7e4b9c32dc296a2583d4c5fa5ad8301
Ending commit: this audit commit; use `git log -1` for the immutable hash.
Worktree at start: clean
Feature readiness verdict: LIMITED

# FULL-CTEST-AUDIT-NONPATH-01

## Scope

This was a maintenance/proof pass after canonical structure cleanup and
`FULL-GATE-LEGACY-TEST-ROUTE-01`. It did not reopen broad structure cleanup and
did not implement runtime, Workbench, renderer, package runtime, provider
runtime, module loader, gameplay, or release publication work.

## Commands

Baseline proof before full CTest:

| Command | Result |
| --- | --- |
| `git diff --check` | PASS |
| `python .aide/scripts/aide_lite.py doctor` | PASS |
| `python .aide/scripts/aide_lite.py validate` | PASS |
| `python tools/validators/repo/check_full_gate_legacy_paths.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_canonical_structure.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict` | PASS |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS, fallback TOML warning only |
| `python tools/validators/testing/check_test_tiers.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict` | PASS_WITH_WARNINGS for archive/historical mentions only |
| `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict` | PASS, 0 violations, 69 warnings |
| `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT` | PASS_WITH_WARNINGS, stale AuditX output warning |
| `cmake --preset verify` | PASS, existing SDL/CMake warnings |
| `cmake --build --preset verify --target ALL_BUILD` | PASS, existing duplicate-symbol linker warnings |
| `ctest --preset verify -L smoke --output-on-failure` | PASS, 57/57 |
| `ctest --preset verify -R "capability_matrix\|capability_regression" --output-on-failure` | PASS, 47/47 |

Full CTest:

| Command | Result |
| --- | --- |
| `ctest --preset verify --output-on-failure` | FAIL, 441/503 passed, 62 failed, exit code 8 |

Evidence:

- `.dominium.local/full-ctest-audit-nonpath-01/full-ctest.log`
- `.dominium.local/full-ctest-audit-nonpath-01/full-ctest-exitcode.txt`
- `.dominium.local/full-ctest-audit-nonpath-01/full-ctest-duration.json`

Full CTest duration was 3144.0196811 seconds.

Targeted reruns after safe path-route fixes:

| Command | Result |
| --- | --- |
| `ctest --preset verify -R "<patched stale-route subset>" --output-on-failure` | FAIL, 18/34 passed, 16 still failing |
| `ctest --preset verify -R "install_manifest_tests" --output-on-failure` | PASS, 1/1 |

## Fixes Performed

The pass repaired clear test/validator route mistakes where a canonical target
already existed. No retired root was recreated.

| Retired expectation | Canonical target |
| --- | --- |
| `tools/schema_migration/schema_migration_runner.py` | `tools/migration/schema/schema_migration_runner.py` |
| `tools/fab/fab_inspect.py` | `tools/domain/fabrication/fab_inspect.py` |
| `tools/fab/fab_validate.py` | `tools/domain/fabrication/fab_validate.py` |
| `tools/fab/fab_diff.py` | `tools/domain/fabrication/fab_diff.py` |
| `tools/securex/securex.py` | `tools/xstack/securex/securex.py` |
| `tools/ops/ops_cli.py` | `tools/package/ops/ops_cli.py` |
| `tools/setup/setup_cli.py` | `tools/package/setup/setup_cli.py` |
| `tools/launcher/launcher_cli.py` | `tools/package/launcher/launcher_cli.py` |
| `tools/share/share_cli.py` | `tools/export/share/share_cli.py` |
| `tools/bugreport/ingest.py` | `tools/diagnostics/bugreport/ingest.py` |
| `tools/bugreport/bugreport_cli.py` | `tools/diagnostics/bugreport/bugreport_cli.py` |
| `engine/include/domino/world/srz_fields.h` | `game/include/domino/world/srz_fields.h` |
| `contracts/schemas/universe/universe_identity.schema` | `contracts/schema/universe/universe_identity.schema` |
| `contracts/schema/authority/authority_context.schema` | `contracts/schema/repo/authority/authority_context.schema` |
| `contracts/schemas/governance/glossary.schema` | `contracts/schema/governance/glossary.schema` |
| `docs/omega/OMEGA_PLAN.md` | `docs/archive/omega/OMEGA_PLAN.md` |
| `tests/perf/perf_guards.json` | `tests/performance/perf_guards.json` |
| `tests/perf/exploration_fixtures/fixtures.json` | `tests/performance/exploration_fixtures/fixtures.json` |

RepoX constants for setup, launcher, package schemas, universe identity,
universe contract bundle, glossary, derived artifact, remediation playbook, and
schema migration registry were also routed to current canonical paths.

## Fixed Tests

These failures from the full run passed after targeted routing:

- `schema_migration_contracts`
- `invariant_srz_execution_modes`
- `test_authority_context_enforcement`
- `test_glossary_consistency`
- `fab_determinism`
- `fab_cycle_policy`
- `fab_recursion`
- `fab_legacy_safety`
- `contentlib_fab_validate`
- `data1_fab_validate`
- `tools_fab_diff`
- `securex_pack_signature_tests`
- `securex_privilege_tests`
- `securex_boundary_tests`
- `securex_reproducible_build_tests`
- `perf_fixture_contracts`
- `exploration_fixture_contracts`
- `bugreport_ingest_tests`
- `install_manifest_tests`

## Remaining Failure Classes

The remaining failures are ledgered in
`docs/repo/audits/FULL_CTEST_NONPATH_FAILURE_LEDGER_01.json`.

| Class | Remaining examples |
| --- | --- |
| `STALE_GENERATED_EVIDENCE` | `dominium_docs_taxonomy`, distribution lockfile baseline |
| `FROZEN_CONTRACT_HASH_MISMATCH` | `const_frozen_contract_hashes` |
| `MISSING_FIXTURE_OR_ASSET` | omega gates, universe state schema, performance budgets, universe complexity docs/schemas |
| `TEST_HARNESS_BUG` | direct-entrypoint import path issues, workspace-scoped RepoX output predicates, raw-path shebang false positives |
| `TRUE_BEHAVIORAL_FAILURE` | process-only mutation, hardcoded IDs/constants, artifact hash path separator instability |
| `EXPECTED_FULL_GATE_DEBT` | client command bridge/session launch and XStack removal proof debt |

## Generated Evidence

Full CTest and targeted security/audit tests modified tracked generated audit
outputs under `docs/audit/**` and `docs/archive/audit/**`, and created
`docs/audit/performance/`. Those files are generated evidence side effects of
the failed audit run, not source edits made by this task. They were not promoted
as canonical proof artifacts by this audit.

## Final Status

Full CTest is not green. The suite now has a more precise signal:

- Baseline fast/current proof remains green or green-with-known-warnings.
- Full CTest completed and failed with 62 failures before fixes.
- Nineteen stale-route failures were repaired and rerun successfully.
- Remaining failures are classified with owners and next actions.
- Broad feature readiness remains blocked; feature readiness remains LIMITED.

## Next Actions

Recommended maintenance tasks:

1. `FULL-GATE-TOOL-ROUTE-02`
2. `FULL-GATE-GENERATED-EVIDENCE-REFRESH-01`
3. `FULL-GATE-FROZEN-CONTRACT-APPROVAL-01`
4. `FULL-GATE-HARNESS-REPAIR-01`
5. `FULL-GATE-BEHAVIOR-REPAIR-01`

Recommended mainline task remains `PROJECTION-CONFORMANCE-01`.
