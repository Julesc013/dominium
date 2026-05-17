# MOVE-BULK-01-APPLY Post-State

## Tracked State

- `data/` tracked files after safe-subset apply: 1,253
- Moved files: 26
- Skipped files: 283
- `git ls-files data` is not empty

## Exception State

`data` remains a tracked root, so no exception was retired or narrowed. All other layout exceptions remain untouched.

## Old-Path State

The exact old paths for the 26 moved files had zero matches before report generation. Remaining Batch A old paths are for skipped files and remain valid because those files were not moved.

## Generated/Local State

`.aide.local/` was used only for temporary scan pattern files and remains ignored/uncommitted.
