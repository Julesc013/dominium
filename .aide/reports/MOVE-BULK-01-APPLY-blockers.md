# MOVE-BULK-01-APPLY Blockers

## Blocking Issues

No global blocker prevented applying the safe subset.

## Skipped Batch A Items

283 of 309 planned Batch A files were skipped because exact-path scanning found active or current references to those old paths. Moving them in this task would have required broader rewrites in active tools, active policy surfaces, protected governance, current docs, or unknown active roots, which this apply task is not authorized to touch.

## Reference Risk Summary

The full Batch A exact-reference scan found:

| Reference class | Matches |
| --- | ---: |
| active or unknown root | 1,444 |
| active policy | 5 |
| active tool | 420 |
| current docs | 1,699 |
| protected governance | 2 |
| unknown | 1 |
| historical or audit | 1 |

The 26 applied files had zero exact old-path matches before they were moved.

## Non-Blocking Warnings

- Batch A remains partial.
- `data/` still has tracked files, so no source-layout exception can retire.
- Broad directory references such as `data/audit` and `data/planning` remain by design because the referenced files were skipped.

## Authorization Status

MOVE-BULK-00-GATE authorized only Batch A safe-subset application. No other batch, import rewrite, shim, exception retirement, or feature work is authorized by this task.
