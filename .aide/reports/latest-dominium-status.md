# Latest Dominium Status

Current task: `RESTRUCTURE-REPAIR-00`.

Result: PARTIAL.

## Current Green State

- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- Strict repo/root/distribution/component validators: PASS.
- Supplemental docs/build/UI/ABI checks: PASS.
- Focused RepoX: PASS.
- Smoke CTest: PASS.
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
- tools_auditx still exceeds the 300 second CTest timeout.
- tracked large AIDE file-quality ledger policy remains unresolved.
- prior repair commits 51257dfdb and 0a579e3c remain commit-policy warning history and were not amended.

DOE-00 readiness: no.

Feature implementation authorized: no.

Next task: `TEST-PERF-01 - CTest Sharding and AuditX Wall-Time Baseline`.
