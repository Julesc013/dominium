# CANON-SPINE-NEW Status

Result: PASS_WITH_WARNINGS.

CANON-SPINE-NEW collapsed the remaining second-level source-spine duplication after the bad-root router work. The task applied broad `git mv` routing, repaired active paths/imports/build references where feasible, and kept generated/local roots out of tracked source.

## Structural Result

- Former configured bad roots: 0 tracked files.
- Staged structural renames before final add: 4,578.
- Scripted CANON-SPINE route applications recorded: 198.
- Scripted route collisions: 0.
- Root-level generated/local tracked files: 0.

## Main Changes

- `runtime/shell/` is the shell/app/appshell/appcore source spine.
- `apps/workbench/` owns user-facing editor/viewer modules.
- `engine/` no longer owns platform/render/store/import/export/install/test buckets as active source.
- `game/domain/`, `content/domains/`, `contracts/schema/`, and `contracts/registry/` are the preferred canonical grammar.
- `tools/` is closer to non-interactive repo/build/codegen/validation tooling.
- Root generated outputs now include `dist/` and `artifacts/` in ignore policy.

## Remaining Warnings

- `scripts/verify_build_target_boundaries.py --repo-root .` still reports boundary warnings.
- Full `cmake --build --preset verify` runs the wider CTest suite and is not green yet.
- New naming validators remain warning-bearing because historical/archive and fixture paths intentionally retain old words.
- Feature work remains blocked.

Next task: `CANON-SPINE-BOUNDARY-01 - Repair Remaining Boundary Imports and Full Proof`.
