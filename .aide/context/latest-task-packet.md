# AIDE Latest Task Packet

## PHASE

MOVE-BULK-08-FINAL-EXCEPTION-CLOSURE - Final Root Exception, Shim, and Bad-Root Closure

## GOAL

Classify the current MOVE-BULK closure state after completed apply evidence and determine readiness for post-restructure proof.

## WHY

The repo must not move to feature work or full proof with ambiguous bad-root, exception, reference, or shim debt.

## CONTEXT_REFS

- `.aide/reports/MOVE-BULK-00-GATE-authorized-batches.json`
- `.aide/reports/MOVE-BULK-00-GATE-readiness.json`
- `.aide/reports/MOVE-BULK-01-APPLY-evidence.json`
- `.aide/reports/MOVE-BULK-08-CLOSURE-root-matrix.json`
- `.aide/reports/MOVE-BULK-08-CLOSURE-remaining-debt.json`
- `docs/repo/root-recycling/MOVE_BULK_08_FINAL_EXCEPTION_CLOSURE.md`

## ALLOWED_PATHS

- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`

## FORBIDDEN_PATHS

- Product/runtime/engine/game/source behavior
- Bad-root file moves, deletes, renames, imports, active references, compatibility shims, active path aliases, unauthorized maps, and feature/domain files

## IMPLEMENTATION

- Inspected 24 formerly bad roots.
- Classified `ide/` as retired/empty.
- Classified 23 former bad roots as remaining tracked debt.
- Retired or narrowed 0 exceptions.
- Created closure matrix, exception actions, reference debt, shim debt, remaining debt, and readiness reports.

## VALIDATION

Run AIDE doctor/validate/test/selftest, AIDE tools/roots/repo/commit checks, closure JSON parsing, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, focused RepoX, and git diff checks.

## EVIDENCE

- `.aide/reports/MOVE-BULK-08-CLOSURE-status.md`
- `.aide/reports/MOVE-BULK-08-CLOSURE-validation.md`
- `.aide/reports/MOVE-BULK-08-CLOSURE-blockers.md`
- `.aide/reports/MOVE-BULK-08-CLOSURE-root-matrix.json`
- `.aide/reports/MOVE-BULK-08-CLOSURE-next-readiness.json`

## NON_GOALS

No moves, deletes, renames, import rewrites, active reference rewrites, shims, map applications, feature work, full CTest, CMake build, product execution, or release generation.

## ACCEPTANCE

- MOVE-BULK-00-GATE evidence exists.
- Every former bad root has a closure state.
- Remaining roots, shims, references, and exception debt are recorded.
- POST-RESTRUCTURE readiness decision is explicit.
- No apply actions occurred.

## OUTPUT_SCHEMA

Evidence is Markdown plus JSON reports under schema prefix `dominium.move_bulk_08.*.v1`.

## TOKEN_ESTIMATE

Compact task packet, under 1,200 tokens.
