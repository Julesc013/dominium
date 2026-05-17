# Latest Warning Disposition

Current task: `RESTRUCTURE-REPAIR-00`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `build/`, `out/`, `dist/`, and `tmp/` are ignored local output and were not staged.
- SDL2 CMake deprecation warnings and missing `PkgConfig` warning remain nonblocking for configure.
- The tracked `.aide/reports/file-quality-ledger.json` large-file policy warning remains unresolved and must not be deleted without evidence.

## Repaired Warnings

- Stale path references in focused tests were repaired.
- TestX fixture host-path literals no longer violate path hygiene.
- Ops compatibility JSON output no longer includes a Python deprecation warning.
- Archive presence now targets archive roots, not retired root paths.
- RepoX archive allowlist now targets the same archive roots.

## Blocking Warnings

- Commit `51257dfdb` failed AIDE commit-message policy because required Markdown headings and `AIDE-Token-Impact` were missing; it was not amended.
- Full CTest is failing/incomplete and cannot be marked green.
- Frozen contract hash drift needs a review-gated hash refresh or doc rollback decision.
- Expired override entries need explicit policy review.
- Replay hash mismatches need deterministic remediation.
- AuditX timeouts need test partitioning or performance repair.

Next task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.
