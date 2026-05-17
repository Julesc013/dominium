# AIDE Latest Review Packet

## Review Objective

Review MOVE-BULK-00-GATE and confirm it authorizes only Batch A safe-subset apply while preserving all no-apply invariants in the gate task.

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

- `.aide/reports/MOVE-BULK-00-GATE-readiness.md`
- `.aide/reports/MOVE-BULK-00-GATE-readiness.json`
- `.aide/reports/MOVE-BULK-00-GATE-validation.md`
- `.aide/reports/MOVE-BULK-00-GATE-blockers.md`
- `.aide/reports/MOVE-BULK-00-GATE-authorized-batches.md`
- `.aide/reports/MOVE-BULK-00-GATE-authorized-batches.json`
- `.aide/reports/MOVE-BULK-00-GATE-deferred-batches.md`
- `.aide/reports/MOVE-BULK-00-GATE-summary.json`
- `docs/repo/root-recycling/MOVE_BULK_00_GLOBAL_BAD_ROOT_MIGRATION_PLAN.md`
- `docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md`

## Changed Files Summary

- Added MOVE-BULK-00-GATE readiness, authorization, deferred, blocker, validation, and summary evidence.
- Updated root-recycling, regression, POST-CONVERGE, AIDE context/status/warning, and migration ledger surfaces.

## Validation Summary

Validation records AIDE checks, plan and gate JSON parsing, TOML fallback/manual inspection, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, and git diff checks. Full eval, full CTest, build, product, package, release, and projection generation are out of scope.

## Risk Summary

Batch A is authorized with safe-subset behavior only. Batches B-G remain deferred, Batch H remains blocked, and feature work remains unauthorized.

## Token Summary

This review packet is intentionally compact and references repo evidence by path.

## Non-Goals / Scope Guard

- no file moves, deletes, renames, import rewrites, reference rewrites, active aliases, compatibility shims, map applications, or exception retirements in this gate
- no edits under target bad roots or product/runtime/source behavior paths
- no generated release/projection/build/local output commits

## Reviewer Instructions

Check that only Batch A is authorized, safe-subset behavior is mandatory, all higher-risk batches remain deferred or blocked, and no apply work occurred.
