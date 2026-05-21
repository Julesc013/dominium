# AIDE Latest Task Packet

## PHASE

foundation-lock-closeout - FOUNDATION-CLOSEOUT-02

## GOAL

Close Foundation Lock after dependency-direction repair and record readiness for the first narrow product slice.

## WHY

Dominium must close the Foundation governance spine before narrow product work begins. Dependency direction, public surface, command, diagnostics, artifact, schema/protocol, capability/refusal, provider, module/app/workbench, replacement, version/deprecation, trust, portability, ABI, AIDE, RepoX, build, and smoke proof must all remain green enough for governed slices.

## CONTEXT_REFS

- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/FOUNDATION_CLOSEOUT_02.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-validation.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-summary.json`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-readiness.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

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
- Workbench/product feature implementation outside closeout scope

## IMPLEMENTATION

- Keep changes scoped to closeout evidence, status, readiness, and narrow stale closeout repairs.
- Do not implement Workbench, gameplay, renderer expansion, native GUI, provider runtime, package runtime, or release publication.
- Keep generated local outputs out of staging.
- Keep broad feature work blocked.

## VALIDATION

- dependency-direction strict: PASS, `0` violations, `68` warnings.
- Foundation validator matrix: PASS.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- RepoX STRICT: PASS with stale AuditX warning.
- FAST strict: PASS, `32` commands, `272.607` seconds.
- CMake configure/build and smoke CTest: PASS through FAST strict.
- full CTest: NOT RUN, T4/full-gate debt.

## COMMITS

Create an audit-grade closeout/evidence commit after validation remains green.

## EVIDENCE

- `docs/repo/audits/FOUNDATION_CLOSEOUT_02.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-*`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## NON_GOALS

- Do not start `WORKBENCH-VALIDATION-SLICE-01` in this task.
- Do not implement Workbench UI, gameplay, renderer expansion, native GUI, runtime module loading, package/provider runtime, or release publication.
- Do not run full CTest unless a targeted blocker requires it.

## ACCEPTANCE

- Foundation Lock is PASS_WITH_WARNINGS.
- `WORKBENCH-VALIDATION-SLICE-01` is authorized as a narrow governed product slice.
- Broad feature work remains blocked.
- Worktree is clean after commit.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `COMMITS`, `VALIDATION`, `PUSH`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 3436
- approx_tokens: 859
- budget_status: PASS
- warnings:
  - none
