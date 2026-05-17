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

## Repairs Applied

- Stale AppShell/client paths updated.
- Integration metadata path updated to `runtime/app/app_runtime.c`.
- Archive manifest paths updated to archive roots.
- RepoX archive allowlist updated to match archive roots.
- TestX host-path fixture sources repaired.
- Ops compatibility JSON output warning repaired.
- RepoX test helper signature updated.
- Narrow pack/lockfile/budget doc contract references added.

## Remaining Blockers

- 23 formerly bad roots remain under active exceptions.
- Full CTest is failing/incomplete.
- Frozen contract hash drift remains.
- Override policy entries are expired.
- Replay hash invariance fails for performance profiles.
- AuditX CTest cases time out.

DOE-00 readiness: no.

Feature implementation authorized: no.

Next task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.
