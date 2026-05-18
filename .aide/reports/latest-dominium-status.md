# Latest Dominium Status

Current task: `TEST-PERF-01`.

Result: PARTIAL with naming law locked and CTest sharding/timing established.

## Current Green State

- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- Strict repo/root/distribution/component validators: PASS.
- Supplemental docs/build/UI/ABI checks: PASS.
- Focused RepoX: PASS.
- Smoke CTest: PASS.
- Fast CTest label: PASS.
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
- full CTest is not green.
- slice0_hardcoded_ids still fails on current hardcoded domain/source/tool/test identifiers.
- slice1_hardcoded_constants still fails on current atmosphere/gravity/oxygen assumptions.
- tools_auditx no longer blocks the 300 second fast lane after TEST-PERF-01; AuditX is now an explicit `audit`/`auditx`/`slow`/`nightly` shard with a 1200 second timeout.
- tracked large AIDE file-quality ledger policy remains unresolved.
- prior repair commits 51257dfdb and 0a579e3c remain commit-policy warning history and were not amended.
- NAME-00 naming conflicts are warning-classified and not moved.

DOE-00 readiness: no.

Feature implementation authorized: no.

Next task: `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS - Hardcoded Identifier and Constant Disposition`.

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
