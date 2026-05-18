# AIDE Review Packet

## Review Objective

Review CANON-SPINE-NEW: broad structural cleanup of second-level source-spine
duplication after bad-root routing.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `.aide/reports/CANON-SPINE-NEW-status.md`
- `.aide/reports/CANON-SPINE-NEW-validation.md`
- `.aide/reports/CANON-SPINE-NEW-blockers.md`
- `.aide/reports/CANON-SPINE-NEW-summary.json`
- `docs/repo/audits/CANON_SPINE_NEW_SOURCE_SPINE_CLEANUP.md`
- `docs/repo/root-recycling/CANON_SPINE_NEW_RESULT.md`
- `docs/repo/final_repository_structure.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## Changed Files Summary

The task moves and repairs active source-spine paths across apps, runtime,
engine, game, contracts, content, docs, tests, tools, release, and archive
surfaces. It also updates AIDE generated-root policy so root generated outputs
do not pollute context while source-owned `tools/build/` remains visible.

## Validation Summary

AIDE and strict layout validators pass. Smoke CTest and focused spine CTest
pass. Build boundary validation and broad full CTest remain follow-up blockers.

## Risk Summary

Remaining risks are stale boundary imports, broader test/proof path drift, and
generated projection/distribution proof refresh. No feature work is authorized.

## Token Summary

The review packet stays compact and references evidence by path.

## Non-Goals / Scope Guard

No feature implementation, public release, tag, upload, semantic ID mutation,
or false full-proof claim.

## Reviewer Instructions

Confirm that former bad roots remain empty, generated/local roots are untracked,
the source spine is materially cleaner, and remaining blockers are assigned to
the next boundary/full-proof task.
