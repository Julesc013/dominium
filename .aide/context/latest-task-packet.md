# AIDE Latest Task Packet

## PHASE

AIDE-MOVE-01-APPLY - first low-risk move application

## GOAL

Apply the single gated move from the former ide README to `docs/architecture/IDE_PROJECTIONS.md`, apply only the six planned reference rewrites, and record validation and rollback evidence.

## WHY

This is the first controlled AIDE move proof. It demonstrates that a small docs-only cleanup can move through plan, gate, apply, reference rewrite, validation, evidence, and rollback recording without broader root cleanup.

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
- `docs/repo/root-recycling/AIDE_MOVE_01_FIRST_LOW_RISK_MOVE_PLAN.md`
- `docs/repo/root-recycling/AIDE_MOVE_01_APPLY_RESULT.md`

## ALLOWED_PATHS

- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`
- `docs/architecture/IDE_PROJECTIONS.md`
- planned reference rewrite files

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
- any move other than the approved README-to-architecture-doc move
- any reference rewrite outside the six planned apply-phase rewrites
- path alias activation, salvage application, move-map application, or exception retirement

## IMPLEMENTATION

- Move the former ide README to `docs/architecture/IDE_PROJECTIONS.md` with `git mv`.
- Apply exactly the six apply-phase rewrites from the reference rewrite plan.
- Do not modify `ide/manifests/**`.
- Do not retire the `ide/` root exception.

## VALIDATION

Run AIDE, strict validators, supplemental docs/build/UI/ABI checks, stale reference search, and git diff checks. Record results in `.aide/reports/AIDE-MOVE-01-APPLY-validation.md`.

## EVIDENCE

- `.aide/reports/AIDE-MOVE-01-APPLY-status.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-evidence.json`
- `.aide/reports/AIDE-MOVE-01-APPLY-validation.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-blockers.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## NON_GOALS

- Do not start another move.
- Do not delete files.
- Do not approve or apply move maps or salvage maps.
- Do not create active aliases or compatibility shims.
- Do not retire exceptions.
- Do not change product/source/runtime/build behavior.

## ACCEPTANCE

- Apply reports and JSON exist.
- The former ide README is absent and `docs/architecture/IDE_PROJECTIONS.md` is present.
- Exactly six planned reference rewrites were applied.
- ide manifests remain untouched.
- Validation passes or only non-blocking known warnings remain.
- No unauthorized move, delete, rename, alias, shim, or exception retirement occurred.

## OUTPUT_SCHEMA

Apply outputs are Markdown and JSON reports under `.aide/reports/**`, plus a root-recycling result doc and optional narrow context/ledger/status updates.

## TOKEN_ESTIMATE

Approximate task packet tokens: 690. No raw source bodies are embedded beyond short path references.
