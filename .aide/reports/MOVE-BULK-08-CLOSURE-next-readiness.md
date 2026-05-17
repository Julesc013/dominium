# MOVE-BULK-08 Next Readiness

Ready for `POST-RESTRUCTURE-00-FULL-PROOF`: **no**.

Feature work authorized: **no**.

## Reasons

- 1764 tracked files remain under formerly bad roots.
- MOVE-BULK gate deferred Batches B-G and blocked Batch H.
- only Batch A has apply evidence, and Batch A still skipped 283 files.
- strict post-restructure full proof has not run.

## Next Recommended Task

`MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`

If the operator wants to skip Batch A refinement, run the next specific batch gate instead; do not apply a deferred batch directly.
