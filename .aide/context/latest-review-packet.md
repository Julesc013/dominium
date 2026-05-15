# AIDE Latest Review Packet

## Review Objective

Review AIDE-MOVE-01-PLAN and decide whether the draft first move plan is ready for AIDE-GATE-02 inspection.

## Decision Requested

Return exactly one of `PASS`, `PASS_WITH_NOTES`, `REQUEST_CHANGES`, or `BLOCKED`.

## Task Packet Reference

- `.aide/context/latest-task-packet.md`

## Context Packet Reference

- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`

## Verification Report Reference

- `.aide/verification/latest-verification-report.md`
- `.aide/verification/review-decision-policy.yaml`

## Evidence Packet References

- `.aide/refactors/AIDE-MOVE-01.plan.toml`
- `.aide/refactors/AIDE-MOVE-01.plan.json`
- `.aide/refactors/AIDE-MOVE-01.reference_rewrite_plan.json`
- `.aide/refactors/AIDE-MOVE-01.validation_plan.json`
- `.aide/refactors/AIDE-MOVE-01.rollback_plan.json`
- `.aide/refactors/AIDE-MOVE-01.exception_update_plan.json`
- `.aide/reports/AIDE-MOVE-01-PLAN-review.md`

## Changed Files Summary

- Added draft no-apply move plan artifacts under `.aide/refactors/`.
- Added AIDE-MOVE-01-PLAN reports under `.aide/reports/`.
- Added root-recycling docs under `docs/repo/root-recycling/`.
- Updated latest AIDE context, ledger, status, and warning disposition.
- No candidate source root files changed.

## Validation Summary

Validation is run by the active task and recorded in `.aide/reports/AIDE-MOVE-01-PLAN-validation.md`.

## Token Summary

This packet is compact and references evidence by path rather than inlining raw source or generated reports.

## Risk Summary

The planned move is one documentation file from the IDE projection root. Manifest schema/examples remain deferred. Apply-phase reference rewrites require gate review, and move application remains unauthorized.

## Non-Goals / Scope Guard

Do not move files, rewrite references, approve maps, apply maps, create aliases, create shims, retire exceptions, or change product/source/runtime/build behavior during review.

## Reviewer Instructions

Check that every plan remains draft, not-approved, and no-apply. Confirm the selected candidate is narrow enough for AIDE-GATE-02 inspection and that deferred manifest metadata remains untouched.
