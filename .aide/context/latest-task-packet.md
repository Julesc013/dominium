# AIDE Latest Task Packet

## PHASE

foundation-lock-repair - FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01

## GOAL

Repair the dependency-direction strict blocker and make the repo ready for `FOUNDATION-CLOSEOUT-02`.

## WHY

Foundation Lock cannot close while dependency-direction strict is red. Workbench and feature work require enforced dependency boundaries between apps, runtime, game, engine, contracts, tools, content, and archive.

## CONTEXT_REFS

- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/FOUNDATION_REPAIR_DEPENDENCY_DIRECTION_01.md`
- `.aide/reports/FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01-validation.md`
- `.aide/reports/FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01-repair-summary.json`
- `.aide/reports/FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01-next-readiness.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `engine/foundation/**`
- `runtime/compatibility/**`
- `runtime/package/**`
- `contracts/repo/dependency_direction_exceptions.toml`
- `docs/repo/**`
- `.aide/context/**`
- `.aide/reports/**`
- `.aide/queue/current.toml`
- `.aide/ledgers/migration_ledger.jsonl`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.dominium.local/**`
- build output roots
- Workbench/product feature implementation outside dependency-direction repair scope

## IMPLEMENTATION

- Keep changes scoped to dependency-direction boundary repair and evidence.
- Do not authorize Workbench or broad feature work.
- Preserve exact transitional exceptions with owners and retirement task.
- Keep generated local outputs out of staging.

## VALIDATION

- dependency-direction strict: PASS, `0` violations, `68` warnings.
- FAST strict: PASS, `32` commands, `312.147` seconds.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS after packet shape is valid.
- RepoX STRICT: PASS with stale AuditX warning.
- CMake configure/build and smoke CTest: PASS through FAST strict.

## COMMITS

Create an audit-grade repair/evidence commit after validation remains green.

## EVIDENCE

- `docs/repo/audits/FOUNDATION_REPAIR_DEPENDENCY_DIRECTION_01.md`
- `.aide/reports/FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01-*`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## NON_GOALS

- Do not start `WORKBENCH-VALIDATION-SLICE-01`.
- Do not implement Workbench UI, gameplay, renderer expansion, native GUI, runtime module loading, package/provider runtime, or release publication.
- Do not run full CTest unless a targeted blocker requires it.

## ACCEPTANCE

- Dependency-direction strict passes.
- FAST strict passes.
- Worktree is clean after commit.
- Next task is `FOUNDATION-CLOSEOUT-02`.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `COMMITS`, `VALIDATION`, `PUSH`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 3144
- approx_tokens: 786
- budget_status: PASS
- warnings:
  - none
