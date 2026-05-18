Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-SCRIPT-00 Bad Root Router Audit

## Status

Result: PASS_WITH_WARNINGS.

MOVE-SCRIPT-00 created a deterministic dry-run router for the remaining former bad roots. It does not authorize physical movement.

## Scope

The task created:

- `tools/migration/route_bad_roots.py`
- `tools/migration/bad_root_routing_rules.json`
- `tools/migration/bad_root_routing_readme.md`

The task generated dry-run routing evidence under `.aide/reports/MOVE-SCRIPT-00-*`.

## Authority Inputs

The router consumes the post-CONVERGE root set, NAME-00 naming canon, layout exceptions, root-recycling runbook, MOVE-BULK batch sequence, RESTRUCTURE-REPAIR-00 final root matrix, and prior MOVE-BULK evidence.

## Dry-Run Result

| Metric | Count |
| --- | ---: |
| Bad-root tracked files scanned | 1,765 |
| Route candidates | 1,593 |
| Skipped/deferred | 172 |
| Target collisions | 0 |

## Candidate Batches

| Batch | Route Candidates | Skipped |
| --- | ---: | ---: |
| B - templates/models/modding | 2 | 4 |
| C - content identity | 1,488 | 26 |
| D - authority/policy | 17 | 33 |
| E - active tools | 0 | 33 |
| F - runtime/core/net | 0 | 54 |
| G - libs/ABI | 86 | 22 |

## Skip Policy

The router skips rather than guesses when a path is active Python/import-sensitive, identity-sensitive without a clear identity-safe target, normative authority material, forbidden by NAME-00 target naming, or otherwise unresolved.

## Non-Apply Proof

- Moves applied: no.
- Deletes applied: no.
- Renames applied: no.
- Imports rewritten: no.
- References rewritten: no.
- Shims created: no.
- Exceptions retired: no.
- Move maps applied: no.
- Salvage maps applied: no.

## Next Task

`MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`

The next gate should consume the route candidates, split unsafe identity/ABI/runtime/policy/import cases, and authorize only exact safe subsets.
