Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Restructure Repair Status

Latest task: `RESTRUCTURE-REPAIR-00`.

Result: PARTIAL.

## Current Green Gates

- AIDE doctor/validate/test/selftest/tools/roots/repo pass.
- Strict layout/root/distribution/component validators pass.
- Focused RepoX passes.
- Smoke CTest passes.
- Native configure and build-only `ALL_BUILD` pass.
- Product boot, portable projection, and internal pilot release validators pass.
- Frozen contract guard passes.
- Override policy tests pass.
- Replay hash invariance passes.

## Current Blockers

- Full CTest is not green.
- Twenty-three formerly bad roots remain under active exceptions.
- `slice0_hardcoded_ids` still fails on current hardcoded identifiers.
- `slice1_hardcoded_constants` still fails on current domain constants.
- `tools_auditx` still exceeds the 300 second CTest timeout.
- The tracked `.aide/reports/file-quality-ledger.json` large-file policy remains unresolved.
- The first two repair evidence commits failed AIDE commit-message policy and were not amended; the follow-up commit records the warnings.

## Next Task

`TEST-PERF-01 - CTest Sharding and AuditX Wall-Time Baseline`

DOE-00 is not ready. Feature implementation remains blocked.
