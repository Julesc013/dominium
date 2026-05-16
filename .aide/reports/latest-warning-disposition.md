# Latest Warning Disposition

## Accepted Warnings

- POST-CONVERGE-10H is PARTIAL because focused tuple `inv_repox_rules` still fails with 153 failures and 5 warnings.
- Canonical `ctest --preset verify -N` still discovers 0 tests; tuple verify remains the effective focused CTest lane.
- Full CTest wall-time remains unproven while focused RepoX still fails.
- Remaining RepoX warnings are unchanged: one stale AuditX output warning and four glossary-term warnings in historical audit/remediation evidence.
- Move planning and move application remain unauthorized.

## Cleared / Reduced

- `INV-CANON-INDEX` is cleared in the after-run counts.
- `INV-DOC-STATUS-HEADER` is reduced from 1545 to 12.
- 1533 clear evidence/reference docs now have valid DERIVED status headers.
- 84 documents that already declared `Status: CANONICAL` are now listed in the canon index.
