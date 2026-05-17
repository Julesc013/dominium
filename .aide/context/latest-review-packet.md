# AIDE Latest Review Packet

## Review Objective

Review MOVE-FAMILY-00-PLAN and confirm that it produced scoped planning evidence only, without moving files, deleting files, renaming files, rewriting references, applying maps, creating aliases, or retiring exceptions.

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

- `.aide/refactors/MOVE-FAMILY-00.plan.toml`
- `.aide/refactors/MOVE-FAMILY-00.plan.json`
- `.aide/refactors/MOVE-FAMILY-00.salvage_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.reference_rewrite_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.validation_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.rollback_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.exception_update_plan.json`
- `.aide/reports/MOVE-FAMILY-00-PLAN-status.md`
- `.aide/reports/MOVE-FAMILY-00-PLAN-validation.md`
- `.aide/reports/MOVE-FAMILY-00-PLAN-blockers.md`
- `.aide/reports/MOVE-FAMILY-00-PLAN-review.md`
- `.aide/reports/MOVE-FAMILY-00-PLAN-summary.json`
- `.aide/reports/MOVE-FAMILY-00-PLAN-candidate-table.md`
- `.aide/reports/MOVE-FAMILY-00-PLAN-candidate-table.json`
- `docs/repo/root-recycling/MOVE_FAMILY_00_GOVERNANCE_META_PERFORMANCE_VALIDATION_IDE_PLAN.md`

## Changed Files Summary

- Added draft/not-approved/no-apply MOVE-FAMILY-00 planning artifacts.
- Classified all current target-family tracked files.
- Recorded that no safe apply set remains after `ide/README.md` was already moved by AIDE-MOVE-01.
- Updated root-recycling, regression, post-converge, latest status, warning disposition, and migration ledger surfaces.

## Validation Summary

MOVE-FAMILY-00-PLAN validation records AIDE checks, plan JSON/TOML parsing, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, and git diff checks. Full CTest, full eval, CMake configure/build, product binary execution, package generation, and release generation remain out of scope.

## Risk Summary

The plan is intentionally blocked for gate readiness. Remaining target-family files are active Python/tooling import surfaces or machine-readable IDE projection metadata; applying moves before ownership and consumer-safe destinations are defined would create avoidable behavioral and validation risk.

## Token Summary

This review packet is intentionally compact and references repo evidence by path.

## Non-Goals / Scope Guard

- no source-root moves, deletes, renames, active aliases, compatibility shims, move-map approvals, move-map applications, salvage-map applications, or exception retirements
- no reference rewrites
- no product/runtime/source behavior changes
- no generated release/projection/build/local output commits
- no full CTest, full eval, package generation, or release generation

## Reviewer Instructions

Check that the diff is limited to scoped planning evidence and documentation, the plan remains draft/not approved/no-apply, and the recommended next task is the active-module boundary refinement rather than `MOVE-FAMILY-00-GATE`.
