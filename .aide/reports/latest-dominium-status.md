# Latest Dominium Status

Current task: `NAME-00 redo after MOVE-SCRIPT-00`.

Result: PARTIAL with naming law redone/refreshed, CTest sharding/timing established, semantic lint blockers resolved, and deterministic bad-root dry-run routing evidence generated.

## Current Green State

- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- Strict repo/root/distribution/component validators: PASS.
- Supplemental docs/build/UI/ABI checks: PASS.
- Focused RepoX: PASS.
- Smoke CTest: PASS.
- Fast CTest label: PASS.
- Semantic lint CTest lanes: PASS.
- AuditX slow shard: PASS.
- Native configure: PASS.
- Native build-only `ALL_BUILD`: PASS.
- Product boot matrix: PASS.
- Portable projection: PASS.
- Internal pilot release validation: PASS.
- Frozen contract guard: PASS.
- Override policy tests: PASS.
- Replay hash invariance: PASS.

## Repairs Applied

- frozen contract hash evidence refreshed from current frozen surfaces.
- expired locklist overrides retired instead of extended.
- performance replay fixture hashes refreshed from current replay stubs.
- AuditX graph/cache scans now ignore local/generated evidence roots.
- AuditX archive-policy analyzers use existing archive-policy report in static scan mode.
- incomplete tracked AuditX JSON and root inventory noise kept out of the commit.
- deterministic bad-root router and routing rules added under `tools/migration/`.
- current bad-root dry run emitted route, skipped, root-summary, and B-G batch-plan evidence without applying moves.

## Remaining Blockers

- 23 excepted former bad roots remain with 1,765 tracked files in the current dry-run router inventory.
- 172 tracked files under former bad roots remain skipped/deferred by MOVE-SCRIPT-00.
- full CTest is still governed by the TEST-PERF-01 sharded execution policy.
- tools_auditx no longer blocks the 300 second fast lane after TEST-PERF-01; AuditX is now an explicit `audit`/`auditx`/`slow`/`nightly` shard with a 1200 second timeout.
- tracked large AIDE file-quality ledger policy remains unresolved.
- prior repair commits 51257dfdb and 0a579e3c remain commit-policy warning history and were not amended.
- NAME-00 naming conflicts are warning-classified and not moved.
- NAME-00 redo confirms 0 naming-law blockers and keeps all naming migrations future-only.

DOE-00 readiness: no.

Feature implementation authorized: no.

Next task: `MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`.

## NAME-00 Additions

- `contracts/repo/naming.contract.toml`
- naming docs under `docs/repo/`
- naming validators under `tools/validators/repo/`
- conflict/readiness evidence under `.aide/reports/NAME-00-*`
- redo snapshot at `148a9adf95bb678da16784434221c568f7bb96cb`, current bad-root inventory 1,765, route candidates 1,593, skipped/deferred 172, collisions 0.

## TEST-PERF-01 Additions

- CTest inventory, timing, shard, AuditX wall-time, blocker, and readiness evidence under `.aide/reports/TEST-PERF-01-*`.
- `docs/testing/CTEST_SHARDING_AND_TIMEOUTS.md`.
- `docs/testing/SLOW_TEST_BASELINE.md`.
- `docs/repo/audits/TEST_PERF_01_CTEST_SHARDING_AUDIT.md`.

## SEMANTIC-LINTS Additions

- `contracts/repo/semantic_lint_allowlist.json`.
- `contracts/repo/semantic_lint_allowlist.schema.json`.
- `docs/testing/SEMANTIC_LINT_DISPOSITION.md`.
- `docs/repo/audits/POST_RESTRUCTURE_REPAIR_SEMANTIC_LINTS.md`.
- semantic lint findings, disposition, allowlist, validation, blocker, and readiness evidence under `.aide/reports/SEMANTIC-LINTS-*`.

## MOVE-SCRIPT-00 Additions

- `tools/migration/route_bad_roots.py`.
- `tools/migration/bad_root_routing_rules.json`.
- `tools/migration/bad_root_routing_readme.md`.
- `docs/repo/audits/MOVE_SCRIPT_00_BAD_ROOT_ROUTER.md`.
- dry-run route, skipped, root-summary, batch-plan, blocker, status, and validation evidence under `.aide/reports/MOVE-SCRIPT-00-*`.
- dry-run summary: 1,765 tracked bad-root files, 1,593 route candidates, 172 skipped/deferred files, 0 target collisions, 0 moves applied.

## MOVE-ROUTER-00 Additions

- `contracts/repo/bad_root_routing.contract.toml`.
- `contracts/repo/bad_root_routing.schema.json`.
- `docs/repo/bad_root_routing.md`.
- `docs/repo/final_repository_structure.md`.
- advisory validators for forbidden names and bad-root absence.
- dry-run route and status evidence under `.aide/reports/MOVE-ROUTER-00-*`.
- dry-run summary: 1,765 tracked bad-root files, 1,765 routed files, 1,694 known canonical routes, 71 quarantine routes, 0 target collisions, 0 skipped/impossible routes, 0 moves applied.

Next task: `MOVE-ROUTER-01 - Apply Deterministic Bad-Root Router Safe Subset`.
