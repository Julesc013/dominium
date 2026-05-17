# Latest Warning Disposition

Current task: `RESTRUCTURE-REPAIR-00`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `build/`, `out/`, `dist/`, and `tmp/` are ignored local output and were not staged.
- SDL2 CMake deprecation warnings and missing `PkgConfig` warning remain nonblocking for configure.
- The tracked `.aide/reports/file-quality-ledger.json` large-file policy warning remains unresolved and must not be deleted without evidence.
- Prior commit-policy warning commits were retained without amendment.

## Repaired Warnings

- frozen contract hash evidence refreshed from current frozen surfaces.
- expired locklist overrides retired instead of extended.
- performance replay fixture hashes refreshed from current replay stubs.
- AuditX graph/cache scans now ignore local/generated evidence roots.
- AuditX archive-policy analyzers use existing archive-policy report in static scan mode.
- incomplete tracked AuditX JSON and root inventory noise kept out of the commit.

## Blocking Warnings

- Full CTest is not green and cannot be marked green.
- `slice0_hardcoded_ids` and `slice1_hardcoded_constants` need doctrine-backed remediation.
- AuditX CTest wall-time needs partitioning or performance repair.
- Remaining excepted bad roots need deferred MOVE-BULK remediation.

Next task: `TEST-PERF-01 - CTest Sharding and AuditX Wall-Time Baseline`.
