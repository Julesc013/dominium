# AIDE Latest Review Packet

## Review Objective

Review MOVE-BULK-00-PLAN and confirm that it creates only a draft no-apply global migration plan for the remaining tracked bad roots.

## Decision Requested

Return exactly one of `PASS`, `PASS_WITH_NOTES`, `REQUEST_CHANGES`, or `BLOCKED`.

## Task Packet Reference

- `.aide/context/latest-task-packet.md`

## Context Packet Reference

- `.aide/context/latest-context-packet.md`

## Verification Report Reference

- `.aide/verification/latest-verification-report.md`
- `.aide/verification/review-decision-policy.yaml`

## Evidence Packet References

- `.aide/refactors/MOVE-BULK-00.global_plan.toml`
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
- `.aide/reports/MOVE-BULK-00-PLAN-*`
- `docs/repo/root-recycling/MOVE_BULK_00_GLOBAL_BAD_ROOT_MIGRATION_PLAN.md`
- `docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md`

## Changed Files Summary

- Added MOVE-BULK-00 global planning artifacts.
- Added one batch JSON plan for each bulk batch A through H.
- Added reviewer-facing status, blocker, root, batch, review, validation, and summary reports.
- Added root-recycling docs for the global plan and batch sequence.
- Updated root-recycling, regression, POST-CONVERGE, AIDE context/status/warning, and migration ledger surfaces.

## Validation Summary

Validation records AIDE checks, JSON/TOML parsing, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, and git diff checks. Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, and projection regeneration remain out of scope.

## Risk Summary

Batch A is gate-ready. Batches B-G remain gated due to identity, authority, import, runtime, or ABI/build sensitivity. Batch H is a final proof/closure batch. The plan is not approved and apply remains disabled.

## Token Summary

This review packet is intentionally compact and references repo evidence by path.

## Non-Goals / Scope Guard

- no moves, deletes, renames, import rewrites, reference rewrites, active aliases, compatibility shims, move-map approvals, salvage-map approvals, map applications, or exception retirements
- no edits under target bad roots or product/runtime/source behavior paths
- no generated release/projection/build/local output commits

## Reviewer Instructions

Check that all generated plans remain draft/not-approved/no-apply, grouped file counts cover the 1,790 tracked bad-root files, no apply action occurred, and the next task is `MOVE-BULK-00-GATE - Global Bad-Root Migration Gate`.
