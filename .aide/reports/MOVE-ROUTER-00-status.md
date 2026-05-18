Status: PASS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-00

# MOVE-ROUTER-00 Status

`MOVE-ROUTER-00` locks the bad-root routing contract and creates a deterministic
dry-run route table. It applies no moves.

## Scope

- Naming canon refreshed for router use.
- Bad-root routing contract created.
- Dry-run router updated to read the routing contract.
- Advisory validators added for forbidden names and bad-root absence.
- Docs and AIDE status surfaces updated.
- No file moves, deletes, renames, imports, references, shims, releases, tags,
  or exception retirements.

## Dry-Run Result

| Metric | Count |
| --- | ---: |
| Bad-root tracked files | 1,765 |
| Routed files | 1,765 |
| Known canonical routes | 1,694 |
| Quarantine routes | 71 |
| Target collisions | 0 |
| Skipped/impossible routes | 0 |
| Sanitized target paths | 3 |
| Import rewrite candidates | 227 |
| Shim candidates | 121 |

## Readiness

The route table is ready for review by:

`MOVE-ROUTER-01 - Apply Deterministic Bad-Root Router Safe Subset`

Feature work and DOE-00 remain blocked.
