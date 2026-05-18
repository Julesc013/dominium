# Latest Dominium Status

Current task: `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS`.

Result: PARTIAL with naming law locked, CTest sharding/timing established, and semantic lint blockers resolved.

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

## Remaining Blockers

- 23 excepted former bad roots remain with 1764 tracked files.
- full CTest is still governed by the TEST-PERF-01 sharded execution policy.
- tools_auditx no longer blocks the 300 second fast lane after TEST-PERF-01; AuditX is now an explicit `audit`/`auditx`/`slow`/`nightly` shard with a 1200 second timeout.
- tracked large AIDE file-quality ledger policy remains unresolved.
- prior repair commits 51257dfdb and 0a579e3c remain commit-policy warning history and were not amended.
- NAME-00 naming conflicts are warning-classified and not moved.

DOE-00 readiness: no.

Feature implementation authorized: no.

Next task: `MOVE-SCRIPT-00 - Generate Deterministic Bad-Root Router and Dry-Run Move Plan`.

## NAME-00 Additions

- `contracts/repo/naming.contract.toml`
- naming docs under `docs/repo/`
- naming validators under `tools/validators/repo/`
- conflict/readiness evidence under `.aide/reports/NAME-00-*`

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
