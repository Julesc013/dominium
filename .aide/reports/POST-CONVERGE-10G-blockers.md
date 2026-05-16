# POST-CONVERGE-10G Blockers

Status: PARTIAL

## Blocking Issues

- Focused tuple `inv_repox_rules` still fails with 1769 failures and 5 warnings.
- POST-CONVERGE-11 product boot proof is still blocked by focused RepoX semantic failures.
- Canonical `ctest --preset verify -N` discovers 0 tests, while tuple CTest remains the effective focused lane.

## Remaining Families

| Invariant | Count | Classification |
| --- | ---: | --- |
| `INV-DOC-STATUS-HEADER` | 1545 | broad documentation status drift |
| `INV-CANON-INDEX` | 84 | missing canonical acceptance/index drift |
| `INV-CANON-NO-HIST-REF` | 81 | historical/generated reference debt |
| `INV-NEW-CONTRACT-REQUIRES-ENTRY` | 9 | authority-sensitive contract acceptance |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 | distribution/product descriptor blocker |
| retired-domain/runtime policy tails | 43 | stale path or real policy blocker by owner |

## Non-Blocking Warnings

- `INV-AUDITX-OUTPUT-STALE` remains one warning.
- `WARN-GLOSSARY-TERM-CANON` remains four warnings for historical audit/remediation evidence.

## Authorization

No move planning, move application, package proof, release proof, portable projection proof, or product boot proof is authorized by this task.
