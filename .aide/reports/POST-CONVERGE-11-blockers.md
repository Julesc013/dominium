# POST-CONVERGE-11 Blockers

Status: DERIVED
Last Reviewed: 2026-05-17

## Blocking Gate

Focused `inv_repox_rules` remains failing with 20 hard failures and 5 warnings. POST-CONVERGE-11 is blocked before product binary discovery or execution.

## Remaining RepoX Families

| Family | Count | Classification |
| --- | ---: | --- |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 | product/projection proof blocker |
| `INV-NO-ADHOC-MAIN` | 5 | product/projection proof blocker |
| MW-4 embodiment fixture import failures | 2 | real non-proof governance/source-policy blocker |
| `INV-REPOX-RULESET-MISSING` | 2 | real non-proof governance blocker |
| `INV-CANON-NO-SUPERSEDED` | 1 | real non-proof canon blocker |
| `INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY` | 1 | real non-proof registry blocker |
| `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN` | 1 | real source-policy blocker |
| `INV-SHADOW-BOUNDED` | 1 | real source-policy blocker |

## Warnings

- `INV-AUDITX-OUTPUT-STALE`: AuditX output is stale.
- Four `WARN-GLOSSARY-TERM-CANON` warnings remain in generated/historical evidence.

## Required Next Action

Run `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation` or a reviewed acceptance gate before retrying product boot proof.
