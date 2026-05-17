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

## Current Blockers

- Full CTest is failing/incomplete.
- Twenty-three formerly bad roots remain under active exceptions.
- Frozen contract hashes are stale.
- Override policy entries are expired.
- Replay hash invariance fails for performance profiles.
- AuditX full CTest cases time out.

## Next Task

`MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`

DOE-00 is not ready. Feature implementation remains blocked.
