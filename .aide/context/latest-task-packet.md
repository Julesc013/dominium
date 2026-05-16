# AIDE Latest Task Packet

## PHASE

AIDE-GATE-03 - post-move proof and next wave readiness gate

## GOAL

Verify the first AIDE-controlled move after apply and decide whether the next move-planning task may proceed.

## WHY

Dominium should not plan another move wave until the first applied move is proven scoped, reference-aware, validator-backed, and reversible.

## CONTEXT_REFS

- `.aide/refactors/AIDE-MOVE-01.plan.json`
- `.aide/refactors/AIDE-MOVE-01.reference_rewrite_plan.json`
- `.aide/refactors/AIDE-MOVE-01.validation_plan.json`
- `.aide/refactors/AIDE-MOVE-01.rollback_plan.json`
- `.aide/refactors/AIDE-MOVE-01.exception_update_plan.json`
- `.aide/reports/AIDE-GATE-02-move-apply-readiness.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-status.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-evidence.json`
- `.aide/reports/AIDE-MOVE-01-APPLY-rollback.md`
- `.aide/reports/AIDE-GATE-03-post-move-readiness.md`
- `.aide/reports/AIDE-GATE-03-post-move-readiness.json`
- `docs/repo/root-recycling/AIDE_MOVE_01_FIRST_LOW_RISK_MOVE_PLAN.md`
- `docs/repo/root-recycling/AIDE_MOVE_01_APPLY_RESULT.md`

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
- ide manifests subtree
- product/version root files
- any file move, delete, rename, or reference rewrite
- path alias activation, salvage application, move-map application, or exception retirement

## IMPLEMENTATION

- Inspect sync state, move evidence, moved-path state, deferred manifests, reference state, exception state, and changed-file scope.
- Run required AIDE, strict validator, supplemental, and git checks.
- Do not modify moved source/target files, manifests, product/source/runtime/build files, maps, aliases, shims, or exception ledgers.

## VALIDATION

Run AIDE, strict validators, supplemental docs/build/UI/ABI checks, stale reference classification, and git diff checks. Record results in `.aide/reports/AIDE-GATE-03-validation.md`.

## EVIDENCE

- `.aide/reports/AIDE-GATE-03-post-move-readiness.md`
- `.aide/reports/AIDE-GATE-03-post-move-readiness.json`
- `.aide/reports/AIDE-GATE-03-validation.md`
- `.aide/reports/AIDE-GATE-03-blockers.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## NON_GOALS

- Do not start another move plan.
- Do not apply another move.
- Do not delete files.
- Do not approve or apply move maps or salvage maps.
- Do not create active aliases or compatibility shims.
- Do not retire exceptions.
- Do not change product/source/runtime/build behavior.

## ACCEPTANCE

- Gate reports and JSON exist.
- The former ide README is absent and `docs/architecture/IDE_PROJECTIONS.md` is present.
- Six planned reference rewrites are verified.
- ide manifests remain untouched.
- Validation passes or only non-blocking known warnings remain.
- No unauthorized move, delete, rename, alias, shim, or exception retirement occurred.
- If passing, only AIDE-MOVE-02 planning is authorized.

## OUTPUT_SCHEMA

Gate outputs are Markdown and JSON reports under `.aide/reports/**`, plus optional narrow context, ledger, status, and first-wave doc updates.

## TOKEN_ESTIMATE

Approximate task packet tokens: 620. No raw source bodies are embedded beyond short path references.
