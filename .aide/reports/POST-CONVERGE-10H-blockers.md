# POST-CONVERGE-10H Blockers

Status: PARTIAL

## Blocking Issues

- Focused tuple `inv_repox_rules` still fails with 153 failures and 5 warnings.
- POST-CONVERGE-11 remains blocked.
- Canonical `ctest --preset verify -N` still discovers 0 tests.

## Remaining RepoX Families

| Family | Count | Notes |
| --- | ---: | --- |
| `INV-CANON-NO-HIST-REF` | 81 | historical/archive reference debt; recommended next target |
| `INV-DOC-STATUS-HEADER` | 12 | deferred authority-sensitive docs |
| `INV-NEW-CONTRACT-REQUIRES-ENTRY` | 9 | contract registry acceptance backlog |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 | distribution/product proof blocker |
| `INV-NO-ADHOC-MAIN` | 5 | distribution/product proof blocker |
| `INV-TOOLS-REQUIRE-ENTITLEMENT` | 5 | retired-domain/tool entitlement path policy |
| other RepoX policy checks | 34 | owner-specific remediation required |

## Warnings

| Warning | Count |
| --- | ---: |
| `WARN-GLOSSARY-TERM-CANON` | 4 |
| `INV-AUDITX-OUTPUT-STALE` | 1 |
