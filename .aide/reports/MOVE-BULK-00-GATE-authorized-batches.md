# MOVE-BULK-00-GATE Authorized Batches

## Authorization Result

Gate result: `PASS_WITH_WARNINGS`.

Only Batch A is authorized for the next apply task.

## Authorized Batch

| Batch | Next Task | Authorization | File Count | Validation |
| --- | --- | --- | ---: | --- |
| Batch A | `MOVE-BULK-01-APPLY-DOCS-ARCHIVE` | `authorize_safe_subset` | 309 | Tier 0 |

## Authorized Scope

Batch A includes only docs/evidence/archive-only material under `data/`:

- `A-DATA-AUDIT`
- `A-DATA-PLANNING`
- `A-DATA-HISTORY`
- `A-DATA-DOCS`
- `A-DATA-META`
- `A-DATA-LOGS`

Apply must use safe-subset behavior:

- apply safe items only;
- defer any item with unexpected active current references;
- do not block all Batch A cleanup because one file/subtree is unsafe;
- preserve historical/audit/generated references when they are classified as historical;
- run Tier 0 validation and stale old-path search after apply.

## Explicit Non-Authorization

No other batch is authorized. No feature work is authorized.

This gate does not authorize moves, deletes, renames, shims, import rewrites, reference rewrites, map application, or exception retirement inside this gate task.
