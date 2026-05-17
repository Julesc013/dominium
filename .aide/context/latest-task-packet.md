# AIDE Latest Task Packet

## PHASE

MOVE-BULK-00-PLAN - Global Bad-Root Migration Plan

## GOAL

Produce one global no-apply migration plan for all remaining tracked bad roots, replacing the remaining micro MOVE-FAMILY planning cadence with batched cleanup waves.

## WHY

The repo has BASELINE-00, RELEASE-00, IDE root retirement proof, and active-tool shim planning evidence. The remaining cleanup needs larger gateable batches so safe docs/evidence/archive material can move quickly while active imports, identity files, authority contracts, runtime/source paths, and ABI/build surfaces remain gated.

## CONTEXT_REFS

- `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`
- `docs/repo/root-recycling/MOVE_BULK_00_GLOBAL_BAD_ROOT_MIGRATION_PLAN.md`
- `docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md`
- `.aide/refactors/MOVE-BULK-00.global_plan.json`
- `.aide/refactors/MOVE-BULK-00.global_salvage_map.json`
- `.aide/refactors/MOVE-BULK-00.global_move_map.json`
- `.aide/refactors/MOVE-BULK-00.global_import_rewrite_map.json`
- `.aide/refactors/MOVE-BULK-00.global_reference_rewrite_map.json`
- `.aide/refactors/MOVE-BULK-00.global_shim_plan.json`
- `.aide/refactors/MOVE-BULK-00.global_exception_retirement_plan.json`
- `.aide/refactors/MOVE-BULK-00.global_validation_plan.json`
- `.aide/refactors/MOVE-BULK-00.global_rollback_plan.json`
- `.aide/refactors/MOVE-BULK-00.batch_*.json`

## ALLOWED_PATHS

- `.aide/refactors/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`

## FORBIDDEN_PATHS

- Remaining bad roots
- `apps/**`, `engine/**`, `game/**`, `runtime/**`, `content/**`, `tests/**`, `tools/**`, `contracts/**`, `cmake/**`, `release/**`
- product/runtime/source behavior paths
- moves, deletes, renames, import rewrites, reference rewrites, active aliases, compatibility shims, approved move maps, approved salvage maps, map applications, or exception retirements

## IMPLEMENTATION

- 23 remaining tracked bad roots inspected.
- 1,790 tracked files classified through grouped salvage entries.
- Batch A docs/evidence/archive-only is ready for gate with 309 files.
- Batches B-G are staged behind owner/import/identity/authority/runtime/ABI gates.
- Batch H is final exception/shim closure and proof.
- `ide/` remains retired and excluded.

## VALIDATION

- AIDE doctor/validate/test/selftest/tools/roots/repo validation.
- AIDE latest commit check.
- JSON/TOML parsing for MOVE-BULK artifacts.
- Strict repo/root/distribution/component validators.
- Docs/build/UI/ABI checks.
- Git diff checks and generated-output staging checks.

## EVIDENCE

- `.aide/reports/MOVE-BULK-00-PLAN-status.md`
- `.aide/reports/MOVE-BULK-00-PLAN-validation.md`
- `.aide/reports/MOVE-BULK-00-PLAN-blockers.md`
- `.aide/reports/MOVE-BULK-00-PLAN-review.md`
- `.aide/reports/MOVE-BULK-00-PLAN-root-summary.md`
- `.aide/reports/MOVE-BULK-00-PLAN-batch-summary.md`
- `.aide/reports/MOVE-BULK-00-PLAN-summary.json`
- `docs/repo/root-recycling/MOVE_BULK_00_GLOBAL_BAD_ROOT_MIGRATION_PLAN.md`
- `docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md`

## NON_GOALS

- No apply task, move operation, source edit, import rewrite, reference rewrite, shim creation, exception retirement, product proof, build, package generation, release generation, or feature work.

## ACCEPTANCE

- All MOVE-BULK-00 plans are draft, not approved, and no-apply.
- Batch/file counts reconcile to 1,790 tracked files.
- Validation evidence records pass/fail/warn outcomes honestly.
- Next task is `MOVE-BULK-00-GATE`.

## OUTPUT_SCHEMA

Primary machine-readable outputs use `dominium.move_bulk_00.*.v1` schemas and plain JSON/TOML.

## TOKEN_ESTIMATE

Compact packet target: under 1,600 tokens.

## NEXT

`MOVE-BULK-00-GATE - Global Bad-Root Migration Gate`.
