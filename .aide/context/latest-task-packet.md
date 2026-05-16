# AIDE Latest Task Packet

## PHASE

AIDE-GATE-02 - move plan apply readiness gate

## GOAL

Inspect the draft AIDE-MOVE-01 plan and decide whether the next task may apply the single planned move.

## WHY

Even a one-file move needs gate review before apply. This gate checks source and target paths, reference rewrites, validation, rollback, exception handling, deferred manifest metadata, and no-apply invariants.

## CONTEXT_REFS

- `.aide/refactors/AIDE-MOVE-01.plan.json`
- `.aide/refactors/AIDE-MOVE-01.reference_rewrite_plan.json`
- `.aide/refactors/AIDE-MOVE-01.validation_plan.json`
- `.aide/refactors/AIDE-MOVE-01.rollback_plan.json`
- `.aide/refactors/AIDE-MOVE-01.exception_update_plan.json`
- `.aide/reports/AIDE-GATE-02-move-apply-readiness.md`
- `docs/repo/root-recycling/AIDE_MOVE_01_FIRST_LOW_RISK_MOVE_PLAN.md`

## ALLOWED_PATHS

- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`

## FORBIDDEN_PATHS

- `apps/**`
- `engine/**`
- `game/**`
- `runtime/**`
- `content/**`
- `tests/**`
- `cmake/**`
- `release/**`
- `ide/README.md`
- `docs/architecture/IDE_PROJECTIONS.md`
- `ide/manifests/**`
- product/version root files
- root move, delete, rename, reference rewrite, path alias activation, salvage application, move-map application, or exception retirement

## IMPLEMENTATION

- Verify the plan only.
- Authorize only `AIDE-MOVE-01-APPLY` if gate criteria pass.
- Do not mutate the original move plan to approved.
- Do not modify source, target, manifest, product, runtime, source, build, or generated behavior files.

## VALIDATION

Run AIDE, plan parse, strict validators, supplemental docs/build/UI/ABI checks, and git diff checks. Record results in `.aide/reports/AIDE-GATE-02-validation.md`.

## EVIDENCE

- `.aide/reports/AIDE-GATE-02-move-apply-readiness.md`
- `.aide/reports/AIDE-GATE-02-move-apply-readiness.json`
- `.aide/reports/AIDE-GATE-02-validation.md`
- `.aide/reports/AIDE-GATE-02-blockers.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## NON_GOALS

- Do not apply the move.
- Do not move, delete, rename, or rewrite files.
- Do not approve or apply move maps or salvage maps.
- Do not create active aliases or compatibility shims.
- Do not retire exceptions.
- Do not authorize any move other than AIDE-MOVE-01-APPLY.

## ACCEPTANCE

- Gate report and JSON exist.
- Gate result is PASS, PASS_WITH_WARNINGS, or BLOCKED.
- If passing, authorization is limited to `ide/README.md -> docs/architecture/IDE_PROJECTIONS.md`.
- Validation passes or only non-blocking known warnings remain.
- No apply action occurred.

## OUTPUT_SCHEMA

Gate outputs are Markdown and JSON reports under `.aide/reports/**`, with optional narrow context, ledger, and root-recycling doc updates.

## TOKEN_ESTIMATE

Approximate task packet tokens: 650. No raw source bodies are embedded beyond short path references.
