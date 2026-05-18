# Latest Warning Disposition

Current task: `NAME-00`.

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
- AuditX CTest wall-time was partitioned by TEST-PERF-01 and now runs under the `auditx` shard.
- Remaining excepted bad roots need deferred MOVE-BULK remediation.
- NAME-00 path, directory, file, and language naming findings are warning-class current debt; they are not proof of cleanup completion.

Next task: `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS - Hardcoded Identifier and Constant Disposition`.

## NAME-00 Warning Disposition

- path-term conflicts: accepted as current warning debt unless a future task creates new unexcepted forbidden roots.
- no-`src`/`source` findings: historical archive or active exception debt, not current authority.
- directory/file naming findings: warning-only until a reviewed enforcement phase.
- language ownership findings: warning-only existing placement debt; no conversion or relocation authorized.
