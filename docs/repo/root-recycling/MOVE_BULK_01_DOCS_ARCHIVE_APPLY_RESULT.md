Status: DRAFT
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-BULK-01 Docs/Archive Apply Result

## Status

MOVE-BULK-01 applied the MOVE-BULK Batch A safe subset with warnings.

- Planned Batch A files: 309.
- Applied safe-subset moves: 26.
- Skipped files: 283.
- Reference rewrites applied: 0.
- Exceptions retired or narrowed: 0.

## Scope

This task used MOVE-BULK-00-GATE authorization for Batch A only. It touched only docs/evidence/archive material from `data/` that had zero exact active/current old-path references.

## Baseline

BASELINE-00 and RELEASE-00 remain the structural regression baseline. This task did not run full CTest, full eval, CMake configure/build, package/release generation, projection generation, or product binaries.

## Moves Applied

The applied safe subset moved:

- one audit evidence file from `data/audit/` to `archive/audits/data/`;
- twenty generated planning data files from `data/planning/` to `docs/planning/generated-data/`;
- five docs-like data files from `data/agents/` and `data/repo/` to `docs/repo/data/`.

The exact file list is recorded in `.aide/reports/MOVE-BULK-01-APPLY-moved-items.md`.

## Skipped Items

283 planned Batch A files were skipped because exact-path scanning found active/current references that this task was not authorized to rewrite. The skipped files remain in their current paths, so those references are not stale.

## Reference Rewrites

No reference rewrites were applied. The 26 moved files had zero exact old-path matches before report generation.

## Exception Updates

No layout exception was retired or narrowed. `git ls-files data` still reports tracked files after the safe-subset apply.

## Validation

Tier 0 validation passed with known TOML fallback-parser warnings in strict validators. The initial AIDE doctor/validate run failed because the latest AIDE task/review packets were missing required sections; those packets were repaired and the rerun passed.

## Rollback

Rollback is limited to reversing the 26 `git mv` operations. No references, imports, shims, exception ledgers, or generated metadata need rollback.

## Remaining Blockers

The skipped Batch A files require a reference-aware follow-up plan or a later apply scope that explicitly authorizes required active tool, active policy, protected governance, and current-doc rewrites.

## Next Task

The next recommended bulk task is `MOVE-BULK-02-APPLY-TEMPLATES-MODELS-MODDING` only if a gate authorizes that batch. Otherwise run a Batch A skipped-reference refinement.
