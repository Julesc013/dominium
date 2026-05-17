# MOVE-BULK-01-APPLY Docs/Archive Status

## Status

- Task ID: `MOVE-BULK-01-APPLY-DOCS-ARCHIVE`
- Batch: A, docs/evidence/archive-only safe subset
- Result: PASS_WITH_WARNINGS
- Branch: `main`
- HEAD before apply: `03af871e4f8f0e9b9ec9c567deefb4cede3b78b0`
- origin/main before apply: `03af871e4f8f0e9b9ec9c567deefb4cede3b78b0`

## Purpose

Batch A is the first bulk cleanup apply wave. It exists to move only passive documentation, historical evidence, generated retained evidence, explanatory notes, and archive-only material out of noncanonical roots while skipping anything that still has active current consumers.

## Authorization

MOVE-BULK-00-GATE authorized `MOVE-BULK-01-APPLY-DOCS-ARCHIVE` for Batch A with safe-subset behavior only. Batches B through G remain deferred, Batch H remains blocked, and feature work remains unauthorized.

## Apply Result

| Metric | Count |
| --- | ---: |
| Batch A planned files | 309 |
| Safe-subset files applied | 26 |
| Files skipped | 283 |
| Reference rewrites applied | 0 |
| Exceptions retired | 0 |
| Exceptions narrowed | 0 |

The first staged full Batch A move was reversed after exact-path scanning found active current references. A narrower second pass moved only the 26 files that had zero exact old-path matches before apply.

## Roots Affected

Only `data/` was affected. `git ls-files data` still reports tracked files, so the `data` layout exception remains unchanged.

## No Unauthorized Work

- Active code changed: no
- Active tool code changed: no
- Imports rewritten: no
- Compatibility shims created: no
- Product/runtime/build files changed: no
- Identity-sensitive files changed: no
- ABI-sensitive files changed: no
- Layout exceptions retired: no

## Next

The next recommended task remains `MOVE-BULK-02-APPLY-TEMPLATES-MODELS-MODDING` if a later gate authorization covers it. The skipped Batch A items need a reference-aware follow-up before they can move.
