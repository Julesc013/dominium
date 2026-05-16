# AIDE Latest Review Packet

## Review Objective

Review AIDE-MOVE-01-APPLY and confirm the first controlled move applied only the gated README move and planned reference rewrites.

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

- `.aide/reports/AIDE-MOVE-01-APPLY-status.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-evidence.json`
- `.aide/reports/AIDE-MOVE-01-APPLY-validation.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-blockers.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-rollback.md`
- `.aide/reports/AIDE-MOVE-01-APPLY-reference-rewrites.md`
- `.aide/refactors/AIDE-MOVE-01.plan.json`
- `.aide/refactors/AIDE-MOVE-01.reference_rewrite_plan.json`

## Changed Files Summary

- Moved the former ide README to `docs/architecture/IDE_PROJECTIONS.md`.
- Applied six planned reference rewrites.
- Added AIDE-MOVE-01-APPLY status, validation, blocker, evidence, rollback, reference rewrite, and post-state reports.
- Added the AIDE-MOVE-01 apply result doc and narrow status/context/ledger updates.
- ide manifests, product/runtime/source/build files, aliases, shims, move maps, salvage maps, and exception ledgers remain untouched.

## Validation Summary

AIDE, strict repo/root/distribution/component validators, docs sanity, build boundary, UI shell, ABI boundary, stale reference search, and git diff checks pass or pass with known non-blocking warnings.

## Token Summary

This packet is compact and references evidence by path rather than inlining raw source or generated reports.

## Risk Summary

The apply passes with warnings because origin/main already matched the local gate commit, Python validator `tomllib` fallback warnings remain, and generated architecture registry references are deferred review items.

## Non-Goals / Scope Guard

Do not start another move, approve maps, apply maps, create aliases, create shims, retire exceptions, or change product/source/runtime/build behavior during review.

## Reviewer Instructions

Confirm that only the approved README-to-architecture-doc move occurred, exactly six planned reference rewrites were applied, ide manifests remained untouched, and the next task should be AIDE-GATE-03.
