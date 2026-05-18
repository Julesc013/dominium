# AIDE Review Packet

## Review Objective

Review MOVE-SCRIPT-00 deterministic bad-root router, routing rules, dry-run evidence, skip/defer ledger, and no-apply compliance.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `.aide/reports/MOVE-SCRIPT-00-status.md`
- `.aide/reports/MOVE-SCRIPT-00-validation.md`
- `.aide/reports/MOVE-SCRIPT-00-blockers.md`
- `.aide/reports/MOVE-SCRIPT-00-routing-preview.json`
- `.aide/reports/MOVE-SCRIPT-00-routing-preview.md`
- `.aide/reports/MOVE-SCRIPT-00-skipped-ledger.json`
- `.aide/reports/MOVE-SCRIPT-00-skipped-ledger.md`
- `.aide/reports/MOVE-SCRIPT-00-root-summary.json`
- `.aide/reports/MOVE-SCRIPT-00-root-summary.md`
- `.aide/reports/MOVE-SCRIPT-00-batch-plan.json`
- `.aide/reports/MOVE-SCRIPT-00-batch-plan.md`
- `tools/migration/route_bad_roots.py`
- `tools/migration/bad_root_routing_rules.json`
- `tools/migration/bad_root_routing_readme.md`
- `docs/repo/audits/MOVE_SCRIPT_00_BAD_ROOT_ROUTER.md`

## Changed Files Summary

MOVE-SCRIPT-00 adds a dry-run-only router that scans tracked bad-root files with `git ls-files`, emits deterministic route/skipped/root/batch evidence, and applies no moves.

## Validation Summary

Expected validation: Python compile/help for the router, router dry-run with collision checks, JSON parse for rules/evidence, AIDE doctor/validate/test/selftest/tools/roots/repo, strict repo/root/distribution/component validators, NAME-00 validators, docs/build/UI/ABI supplemental checks, focused RepoX, smoke CTest, and git diff checks.

## Risk Summary

The route candidate set is intentionally conservative. Skipped files remain deferred where import rewrites, shims, identity proof, authority review, ABI/build proof, or naming-risk review is required.

## Token Summary

The task and review packets stay compact and reference evidence by path instead of embedding full CTest output.

## Non-Goals / Scope Guard

No root movement, deletion, rename, reference rewrite, import rewrite, shim, layout exception retirement, product/runtime feature work, release generation, public release, tag, or generated local output commit.

## Reviewer Instructions

Check that the router is dry-run-only by default, every planned target is deterministic, collisions are refused, skipped/deferred reasons are explicit, and no filesystem move or exception retirement occurred.
