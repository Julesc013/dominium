# FOUNDATION-CLOSEOUT-01 Validation

## Sync And Doctrine

- PASS: `git status --short --branch` reported `## main...origin/main` at start.
- PASS: `git fetch --all --prune`.
- PASS: `git rev-parse HEAD` -> `6f12e6f0a89a789d894a790970c8c18980312dba`.
- PASS: `git rev-parse origin/main` -> `6f12e6f0a89a789d894a790970c8c18980312dba`.
- PASS: both ancestry checks reported HEAD and origin/main as mutual ancestors.
- PASS: required AGENTS/doctrine packet files exist and were sampled before validation.
- PASS: `py -3 .aide/scripts/aide_lite.py doctor`.
- PASS: `py -3 .aide/scripts/aide_lite.py validate` with existing review-reference warnings only.
- PASS: `py -3 .aide/scripts/aide_lite.py pack --task "FOUNDATION-CLOSEOUT-01"`.

## Foundation Validators

- PASS: `python tools/validators/testing/check_test_tiers.py --repo-root . --strict` -> test tier contract validation PASS.
- PASS: `python tools/validators/repo/check_public_surface.py --repo-root . --strict` -> 148 surfaces, 2 stable, 25 kinds, 12 stability classes.
- PASS_WITH_WARNINGS: `python tools/validators/abi/check_public_headers.py --repo-root . --strict` -> PASS, 375 headers, 0 errors, 2851 warnings.
- FAIL: `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict` -> 358 violations, 38 warnings.
- PASS: `python tools/validators/contracts/check_command_surface.py --repo-root . --strict` -> 5 commands, 0 errors, 0 warnings.
- PASS: `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict` -> 89 diagnostic codes, 0 errors, 0 warnings.
- PASS: `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict` -> 23 artifact kinds, 11 lifecycle states.
- PASS: `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict`.
- PASS: `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict` -> 30 capabilities, 44 refusal codes.
- PASS: `python tools/validators/contracts/check_provider_model.py --repo-root . --strict` -> 5 providers, 15 provider kinds.
- PASS: `python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict` -> 12 module kinds.
- PASS: `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`.
- PASS: `python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict`.
- PASS: `python tools/validators/repo/check_replacement_packet.py --repo-root . --strict` -> 19 replacement kinds, 10 statuses.
- PASS: `python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict` -> 9 lifecycle states.
- PASS: `python tools/validators/package/check_mod_pack_trust.py --repo-root . --strict` -> 7 trust levels, 22 permission kinds.
- PASS: `python tools/validators/platform/check_portability_matrix.py --repo-root . --strict` -> 8 platform floors, 6 architectures, 10 toolchains.

## Fixtures

- PASS: artifact identity fixtures.
- PASS: schema/protocol evolution fixtures.
- PASS: capability/refusal fixtures.
- PASS: provider fixtures, count 9.
- PASS: module fixtures, count 6.
- PASS: workbench fixtures, count 5.
- PASS: app fixtures, count 4.
- PASS: replacement fixtures, 4 valid and 4 invalid.
- PASS: version/deprecation fixtures, 3 valid and 4 invalid.
- PASS: mod/pack trust fixtures, 10 expected outcomes.
- PASS: portability fixtures, 4 valid and 4 invalid.

## Inventory

- WARN: provider inventory scanned 18066 files.
- PASS: module/workbench/app inventory modes completed.
- WARN: replacement inventory found 1852 replacement-like files.
- WARN: version/deprecation inventory found 2511 version-like files.
- WARN: mod/pack trust inventory is descriptive and current packs are not migrated by the validator.
- PASS: portability inventory completed with build, smoke, product, release, planned, research, historical, and deferred buckets.

## Fast Strict

- FAIL: first closeout fast strict attempt failed at `t1.repox_strict` because `docs/repo/audits/PORTABILITY_MATRIX_01.md` missed the required status header shape.
- FAIL: second attempt still failed at `t1.repox_strict` because the same audit used task result text as the canonical document status value.
- REPAIR: `docs/repo/audits/PORTABILITY_MATRIX_01.md` now uses `Status: DERIVED` and keeps `Result: PASS_WITH_WARNINGS` separately.
- PASS: final fast strict rerun passed 32 commands in 308.406 seconds.
- PASS: RepoX STRICT passed in the final fast strict run.
- PASS: CMake configure/build passed in the final fast strict run.
- PASS: smoke CTest passed in the final fast strict run.
- Latest evidence: `.aide/reports/FOUNDATION-CLOSEOUT-01-fast-strict.md`.

## Not Run

- NOT RUN: full CTest. It remains T4/full-gate debt.
