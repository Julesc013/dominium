Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-SCRIPT-00 Status

Result: PASS_WITH_WARNINGS.

MOVE-SCRIPT-00 added a deterministic dry-run router for the remaining former bad roots.

## Dry-Run Result

- Bad-root tracked files scanned: 1,765.
- Route candidates emitted: 1,593.
- Skipped/deferred items: 172.
- Target collisions: 0.
- Files moved: 0.
- Files deleted: 0.
- Files renamed: 0.
- References rewritten: 0.
- Shims created: 0.
- Exceptions retired: 0.

## Router Artifacts

- `tools/migration/route_bad_roots.py`
- `tools/migration/bad_root_routing_rules.json`
- `tools/migration/bad_root_routing_readme.md`

## Evidence

- `.aide/reports/MOVE-SCRIPT-00-routing-preview.json`
- `.aide/reports/MOVE-SCRIPT-00-routing-preview.md`
- `.aide/reports/MOVE-SCRIPT-00-skipped-ledger.json`
- `.aide/reports/MOVE-SCRIPT-00-skipped-ledger.md`
- `.aide/reports/MOVE-SCRIPT-00-root-summary.json`
- `.aide/reports/MOVE-SCRIPT-00-root-summary.md`
- `.aide/reports/MOVE-SCRIPT-00-batch-plan.json`
- `.aide/reports/MOVE-SCRIPT-00-batch-plan.md`

## Next Task

`MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`

This task does not authorize applying the route candidates.
