# Latest Dominium AIDE Status

## Status

- POST-CONVERGE-10G: PARTIAL, RepoX reduced from 1844 to 1769 failures
- POST-CONVERGE-10H: PARTIAL, RepoX reduced from 1769 to 153 failures
- `INV-DOC-STATUS-HEADER`: 1545 -> 12
- `INV-CANON-INDEX`: 84 -> 0
- Move planning authorized: false
- Move application authorized: false
- Product boot proof authorized: false

## Current Blocker

Focused tuple `inv_repox_rules` still fails with 153 failures and 5 warnings. The largest remaining family is `INV-CANON-NO-HIST-REF` with 81 failures.

## No-Move Confirmation

POST-CONVERGE-10H did not move, delete, rename, rewrite broad references, apply maps, create aliases, retire exceptions, or change product/runtime/source behavior.

## Next Task

`POST-CONVERGE-10I - Historical Reference and Archive Citation Remediation`.
