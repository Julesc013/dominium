# POST-CONVERGE-10O Blockers

Status: DERIVED
Last Reviewed: 2026-05-17

## Hard Failures

| Family | Count | Classification | Disposition |
| --- | ---: | --- | --- |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 | product/projection proof blocker | Deferred until product/projection wrapper proof after non-proof blockers are handled. |
| `INV-NO-ADHOC-MAIN` | 5 | product/projection proof blocker | Deferred until product/projection wrapper proof after non-proof blockers are handled. |
| MW-4 fixture import failures through `game.domain.embodiment` | 2 | real governance/source-policy blocker | Needs residual RepoX remediation. |
| `INV-REPOX-RULESET-MISSING` | 2 | real governance/ruleset blocker | Needs mapping or explicit classification. |
| `INV-CANON-NO-SUPERSEDED` | 1 | real governance/canon blocker | Needs canon/supersession review. |
| `INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY` | 1 | real governance/registry blocker | Needs registry entry or explicit classification. |
| `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN` | 1 | real source-policy blocker | Needs source-policy remediation or explicit acceptance. |
| `INV-SHADOW-BOUNDED` | 1 | real source-policy blocker | Needs source-policy remediation or explicit acceptance. |

## Warnings

- `INV-AUDITX-OUTPUT-STALE`: AuditX findings are stale by 201 commits.
- Four `WARN-GLOSSARY-TERM-CANON` warnings remain in generated/historical audit evidence.

## Gate

POST-CONVERGE-11 is blocked by the non-proof hard failures above.
