# AIDE Review Packet

## Review Objective

Review MOVE-ROUTER-00: naming/routing contracts, dry-run router behavior, complete bad-root route table, quarantine fallback, advisory validators, status updates, and no-apply compliance.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `contracts/repo/naming.contract.toml`
- `contracts/repo/bad_root_routing.contract.toml`
- `contracts/repo/bad_root_routing.schema.json`
- `tools/migration/route_bad_roots.py`
- `docs/repo/bad_root_routing.md`
- `docs/repo/final_repository_structure.md`
- `.aide/reports/MOVE-ROUTER-00-dry-run.json`
- `.aide/reports/MOVE-ROUTER-00-route-table.json`
- `.aide/reports/MOVE-ROUTER-00-target-collisions.md`
- `.aide/reports/MOVE-ROUTER-00-validation.md`
- `.aide/reports/MOVE-ROUTER-00-status.md`
- `.aide/reports/MOVE-ROUTER-00-blockers.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## Changed Files Summary

The task adds the routing contract, router dry-run behavior, route reports, advisory validators, docs, and status surfaces. It does not move, delete, rename, rewrite, shim, apply maps, retire exceptions, or change product/runtime/content behavior.

## Validation Summary

Expected validation: router dry-run with collision check, new advisory validators, AIDE doctor/validate/test/selftest/tools/roots/repo, strict repo/root/distribution/component validators, Python compile for new router/validators, JSON/TOML parse checks, docs/build/UI/ABI checks, and git diff checks.

## Risk Summary

The route table is dry-run evidence only. Quarantine routes and import/shim candidates remain apply-task risks. The task does not authorize feature work or MOVE-ROUTER-01 application by itself.

## Token Summary

The task and review packets stay compact and reference evidence by path instead of embedding full validator output.

## Non-Goals / Scope Guard

No root movement, deletion, rename, reference rewrite, import rewrite, shim, layout exception retirement, feature work, generated local output commit, package/release generation, tag, or GitHub release.

## Reviewer Instructions

Confirm that every tracked bad-root file receives a route, target collisions are zero, unknown files route to quarantine, and no apply-side filesystem changes occurred.
