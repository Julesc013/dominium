# AIDE Latest Task Packet

## PHASE

MOVE-BULK-00-GATE - Global Bad-Root Migration Gate

## GOAL

Review the MOVE-BULK-00 global bad-root migration plan and authorize only specific safe apply batches.

## WHY

The global plan is intentionally aggressive. The gate limits apply authorization to the safest scope so cleanup can move quickly without bypassing BASELINE-00 regression requirements.

## CONTEXT_REFS

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
- `.aide/reports/MOVE-BULK-00-GATE-*`
- `docs/repo/root-recycling/MOVE_BULK_00_GLOBAL_BAD_ROOT_MIGRATION_PLAN.md`
- `docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md`

## ALLOWED_PATHS

- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`

## FORBIDDEN_PATHS

- target bad-root files
- `apps/**`, `engine/**`, `game/**`, `runtime/**`, `content/**`, `tests/**`, `tools/**`, `contracts/**`, `cmake/**`, `release/**`
- moves, deletes, renames, import rewrites, reference rewrites, active aliases, compatibility shims, move-map approvals outside gate scope, salvage-map approvals outside gate scope, map applications, or exception retirements

## IMPLEMENTATION

- Global and batch artifacts parse and remain draft/not-approved/no-apply.
- Batch A is authorized as `MOVE-BULK-01-APPLY-DOCS-ARCHIVE`.
- Batches B-G are deferred.
- Batch H is blocked until prior apply/proof tasks complete.

## VALIDATION

- AIDE doctor/validate/test/selftest/tools/roots/repo validation.
- AIDE latest commit check.
- MOVE-BULK plan and gate JSON parsing.
- TOML parse if available; otherwise manual inspection.
- Strict repo/root/distribution/component validators.
- Docs/build/UI/ABI checks.
- Git diff checks.

## EVIDENCE

- `.aide/reports/MOVE-BULK-00-GATE-readiness.md`
- `.aide/reports/MOVE-BULK-00-GATE-readiness.json`
- `.aide/reports/MOVE-BULK-00-GATE-validation.md`
- `.aide/reports/MOVE-BULK-00-GATE-blockers.md`
- `.aide/reports/MOVE-BULK-00-GATE-authorized-batches.md`
- `.aide/reports/MOVE-BULK-00-GATE-authorized-batches.json`
- `.aide/reports/MOVE-BULK-00-GATE-deferred-batches.md`
- `.aide/reports/MOVE-BULK-00-GATE-summary.json`

## NON_GOALS

- No apply work, file moves, deletion, renames, import rewrites, reference rewrites, shim creation, exception retirement, product proof, build, package generation, release generation, or feature work.

## ACCEPTANCE

- Authorized batches are explicit.
- Safe-subset apply behavior is mandatory.
- Validation evidence records pass/warn/fail honestly.
- Next task is the first authorized apply task.

## OUTPUT_SCHEMA

Gate JSON outputs use `dominium.move_bulk_00.gate_*.v1` schemas.

## TOKEN_ESTIMATE

Compact packet target: under 1,600 tokens.

## NEXT

`MOVE-BULK-01-APPLY-DOCS-ARCHIVE`.
