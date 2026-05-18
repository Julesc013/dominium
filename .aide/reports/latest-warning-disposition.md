# Latest Warning Disposition

Current task: `NAME-00 redo after MOVE-SCRIPT-00`.

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
- `slice0_hardcoded_ids` and `slice1_hardcoded_constants` now pass with exact-match semantic lint dispositions.

## Blocking Warnings

- Full CTest remains governed by the TEST-PERF-01 sharded execution policy.
- AuditX CTest wall-time was partitioned by TEST-PERF-01 and now runs under explicit `audit`/`auditx`/`slow`/`nightly` shards.
- Remaining excepted bad roots need deferred MOVE-BULK remediation.
- NAME-00 path, directory, file, and language naming findings are warning-class current debt; they are not proof of cleanup completion.
- NAME-00 redo confirms zero blocker-class naming findings and updates the current conflict posture against `148a9adf95bb678da16784434221c568f7bb96cb`.
- MOVE-SCRIPT-00 skipped/deferred 172 tracked bad-root files that require import, identity, authority, ABI/build, or naming-risk review before any apply task.
- Initial MOVE-SCRIPT-00 implementation commit `a4425775f` failed latest-commit policy because the message omitted `## Changelog`; it was not amended and is followed by a scoped policy-disposition commit.

Next task: `MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`.

## SEMANTIC-LINTS Warning Disposition

- 1,104 reproduced findings were classified before allowlisting.
- The semantic lint allowlist is exact-match only: test name, file, line, validator message, and source-line hash.
- No broad wildcard, directory-wide, docs-wide, or message-class suppression was added.
- Future hardcoded identifier/constant findings remain blockers until fixed or narrowly justified.

## TEST-PERF-01 Warning Disposition

- Full CTest remains governed by TEST-PERF-01 sharding. The former semantic lint blockers were resolved by POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS.
- AuditX is accepted as a bounded slow/nightly shard, not as a fast local lane.
- Dirty changed paths that do not match explicit XStack group paths now fall back to core TestX/AuditX groups so impacted FULL plans do not silently lose shards.

## NAME-00 Warning Disposition

- path-term conflicts: accepted as current warning debt unless a future task creates new unexcepted forbidden roots.
- no-`src`/`source` findings: historical archive or active exception debt, not current authority.
- directory/file naming findings: warning-only until a reviewed enforcement phase.
- language ownership findings: warning-only existing placement debt; no conversion or relocation authorized.
- current redo counts: 106 no-src/source findings, 1,450 forbidden path-term findings, 418 directory naming findings, 5,361 file naming findings, and 4 language ownership finding classes, all with 0 blockers.

## MOVE-SCRIPT-00 Warning Disposition

- Router result is `PASS_WITH_WARNINGS` because dry-run planning found deferred files, not because the router failed.
- `active_python_package_requires_import_rewrite_or_shim_plan` remains deferred to an explicitly authorized active-tool/runtime apply plan.
- `identity_sensitive_without_clear_identity_safe_route` remains deferred to identity-safe content/package/profile/bundle proof.
- `authority_sensitive_docs_only_route_requires_review` and `normative_specs_reality_docs_require_authority_review` remain deferred to authority review.
- forbidden target segments such as `source` and generic `compat` are refused by the router and require refined target ownership before apply.
- Target collisions are currently zero.
