# AIDE Latest Review Packet

## Review Objective

Review MOVE-FAMILY-00B-PLAN and confirm that it creates only a draft no-apply plan for `ide/manifests/**`, without moving files, deleting files, renaming files, rewriting references, creating shims, applying maps, or retiring exceptions.

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

- `.aide/refactors/MOVE-FAMILY-00B.plan.toml`
- `.aide/refactors/MOVE-FAMILY-00B.plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.ide_manifest_inventory.json`
- `.aide/refactors/MOVE-FAMILY-00B.ide_manifest_ownership.json`
- `.aide/refactors/MOVE-FAMILY-00B.reference_rewrite_plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.validation_plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.rollback_plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.exception_update_plan.json`
- `.aide/reports/MOVE-FAMILY-00B-PLAN-status.md`
- `.aide/reports/MOVE-FAMILY-00B-PLAN-validation.md`
- `.aide/reports/MOVE-FAMILY-00B-PLAN-blockers.md`
- `.aide/reports/MOVE-FAMILY-00B-PLAN-review.md`
- `.aide/reports/MOVE-FAMILY-00B-PLAN-manifest-boundaries.md`
- `.aide/reports/MOVE-FAMILY-00B-PLAN-summary.json`
- `docs/repo/root-recycling/MOVE_FAMILY_00B_IDE_MANIFEST_CONTRACT_PROJECTION_PLAN.md`

## Changed Files Summary

- Added MOVE-FAMILY-00B planning artifacts for inventory, ownership, reference rewrites, validation, rollback, exception updates, and plan JSON/TOML.
- Added reviewer-facing MOVE-FAMILY-00B reports.
- Added repo root-recycling plan doc for IDE manifest contract/projection ownership.
- Updated root-recycling, regression, AIDE context, status, warning, and migration ledger surfaces.

## Validation Summary

Validation records AIDE checks, artifact JSON/TOML parsing, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, and git diff checks. Full CTest, full eval, CMake configure/build, product binary execution, package generation, and release generation remain out of scope.

## Risk Summary

The plan is gate-ready but not approved. `contracts/projections/ide/**` does not exist yet and must be introduced only during a later approved apply task. Generated projection manifest output under `ide/manifests/*.projection.json` remains a separate ignored-output policy concern.

## Token Summary

This review packet is intentionally compact and references repo evidence by path.

## Non-Goals / Scope Guard

- no source-root moves, deletes, renames, reference rewrites, active aliases, compatibility shims, move-map approvals, salvage-map approvals, map applications, or exception retirements
- no edits under `ide/**`, `contracts/**`, `tools/**`, or product/runtime/source behavior paths
- no generated release/projection/build/local output commits
- no full CTest, full eval, package generation, or release generation

## Reviewer Instructions

Check that the diff is limited to scoped planning evidence and documentation, apply remains disabled, and the recommended next task is `MOVE-FAMILY-00B-GATE - IDE Manifest Projection Apply Readiness Gate`.

## MOVE-FAMILY-00B-GATE REVIEW UPDATE

- Gate result: PASS_WITH_WARNINGS.
- Gate evidence:
  - `.aide/reports/MOVE-FAMILY-00B-GATE-readiness.md`
  - `.aide/reports/MOVE-FAMILY-00B-GATE-readiness.json`
  - `.aide/reports/MOVE-FAMILY-00B-GATE-validation.md`
  - `.aide/reports/MOVE-FAMILY-00B-GATE-blockers.md`
- Authorized next task: `MOVE-FAMILY-00B-APPLY - Apply IDE Manifest Projection Migration`.
- Authorized scope: the three planned moves from `ide/manifests/**` to `contracts/projections/ide/**`.
- All other root moves remain unauthorized.
- No files were moved, deleted, renamed, reference-rewritten, or exception-retired by the gate.

## MOVE-FAMILY-00B-APPLY REVIEW UPDATE

- Apply result: PASS_WITH_WARNINGS.
- Evidence:
  - `.aide/reports/MOVE-FAMILY-00B-APPLY-status.md`
  - `.aide/reports/MOVE-FAMILY-00B-APPLY-validation.md`
  - `.aide/reports/MOVE-FAMILY-00B-APPLY-blockers.md`
  - `.aide/reports/MOVE-FAMILY-00B-APPLY-evidence.json`
  - `.aide/reports/MOVE-FAMILY-00B-APPLY-reference-rewrites.md`
  - `.aide/reports/MOVE-FAMILY-00B-APPLY-post-state.md`
  - `.aide/reports/MOVE-FAMILY-00B-APPLY-rollback.md`
- Reviewed state: three moves applied, five rewrite groups applied, `git ls-files ide` empty, `ide_root` retired.
- Next review target: `MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof`.

## MOVE-FAMILY-00B-PROOF REVIEW UPDATE

- Proof result: PASS_WITH_WARNINGS.
- Evidence:
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-status.md`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-validation.md`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-blockers.md`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-root-retirement.json`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-reference-classification.md`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-reference-classification.json`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-baseline-regression.md`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-next-readiness.md`
  - `.aide/reports/MOVE-FAMILY-00B-PROOF-next-readiness.json`
  - `docs/repo/root-recycling/MOVE_FAMILY_00B_IDE_ROOT_RETIREMENT_PROOF.md`
- Reviewed state: `git ls-files ide` empty, filesystem `ide/` absent, `ide_root` retired, moved manifests parse, no active stale source/tool/validator blockers.
- Next review target: `MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan`.

## MOVE-FAMILY-00C-PLAN REVIEW UPDATE

- Plan result: BLOCKED.
- Evidence:
  - `.aide/refactors/MOVE-FAMILY-00C.plan.json`
  - `.aide/refactors/MOVE-FAMILY-00C.active_tool_inventory.json`
  - `.aide/refactors/MOVE-FAMILY-00C.import_reference_map.json`
  - `.aide/refactors/MOVE-FAMILY-00C.ownership_map.json`
  - `.aide/refactors/MOVE-FAMILY-00C.shim_plan.json`
  - `.aide/reports/MOVE-FAMILY-00C-PLAN-status.md`
  - `.aide/reports/MOVE-FAMILY-00C-PLAN-validation.md`
  - `.aide/reports/MOVE-FAMILY-00C-PLAN-blockers.md`
  - `.aide/reports/MOVE-FAMILY-00C-PLAN-review.md`
  - `.aide/reports/MOVE-FAMILY-00C-PLAN-active-tool-boundaries.md`
  - `.aide/reports/MOVE-FAMILY-00C-PLAN-import-map.md`
  - `.aide/reports/MOVE-FAMILY-00C-PLAN-summary.json`
  - `docs/repo/root-recycling/MOVE_FAMILY_00C_ACTIVE_TOOL_NAMESPACE_PLAN.md`
- Reviewed state: 33 active Python files remain across validation/meta/governance/performance; no direct CLI entrypoints; no apply-ready batch.
- Gate readiness: false.
- Next review target: `MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan`.

## MOVE-FAMILY-00C-A-PLAN REVIEW UPDATE

- Plan result: PASS_WITH_WARNINGS.
- Evidence:
  - `.aide/refactors/MOVE-FAMILY-00C-A.plan.json`
  - `.aide/refactors/MOVE-FAMILY-00C-A.package_inventory.json`
  - `.aide/refactors/MOVE-FAMILY-00C-A.import_consumers.json`
  - `.aide/refactors/MOVE-FAMILY-00C-A.target_namespace_map.json`
  - `.aide/refactors/MOVE-FAMILY-00C-A.shim_contract.json`
  - `.aide/refactors/MOVE-FAMILY-00C-A.import_rewrite_plan.json`
  - `.aide/refactors/MOVE-FAMILY-00C-A.static_check_plan.json`
  - `.aide/reports/MOVE-FAMILY-00C-A-PLAN-status.md`
  - `.aide/reports/MOVE-FAMILY-00C-A-PLAN-validation.md`
  - `.aide/reports/MOVE-FAMILY-00C-A-PLAN-blockers.md`
  - `.aide/reports/MOVE-FAMILY-00C-A-PLAN-review.md`
  - `.aide/reports/MOVE-FAMILY-00C-A-PLAN-shim-contract.md`
  - `.aide/reports/MOVE-FAMILY-00C-A-PLAN-import-consumers.md`
  - `.aide/reports/MOVE-FAMILY-00C-A-PLAN-summary.json`
  - `docs/repo/root-recycling/MOVE_FAMILY_00C_A_VALIDATION_IDENTITY_STABILITY_SHIM_PLAN.md`
- Reviewed state: 7 implementation files planned for a later apply, 7 temporary shim files planned, 34 import rewrites planned, and 10 old-import callers temporarily allowlisted.
- Gate readiness: true.
- Next review target: `MOVE-FAMILY-00C-A-GATE - Validation, Identity, and Stability Shim Migration Gate`.
