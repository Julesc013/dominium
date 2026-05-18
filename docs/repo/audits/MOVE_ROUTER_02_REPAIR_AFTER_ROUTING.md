# MOVE-ROUTER-02 Repair After Routing Audit

Status: PARTIAL
Generated: 2026-05-18

## Scope

MOVE-ROUTER-02 repaired references, imports, build paths, validator expectations,
and root-state evidence after MOVE-ROUTER-01 physically moved tracked files out
of the former bad roots.

## Repairs Applied

- Preserved the MOVE-ROUTER-01 structural result: former bad roots remain empty.
- Recorded 33,316 exact path replacements across 1,171 files.
- Recorded 76 import replacements across 74 Python files.
- Promoted active ABI/build/runtime files from quarantine into canonical owners
  where build ownership was clear.
- Created three temporary runtime control shim packages.
- Repaired CMake ownership for DOM contracts, build identity, Win32 UI backend,
  and legacy library aggregation.
- Repaired selected active test and XStack registry paths.

## Validation

- Bad-root absence: PASS.
- Strict repo layout: PASS.
- Strict root allowlist: PASS.
- CMake configure: PASS.
- Build: PARTIAL.
- Integrated fast/smoke tests reached by build: PASS, 57/57.
- Broader TestX: FAIL, 140/344 failed.
- `git diff --check`: PASS.

## Remaining Blockers

- RepoX ruleset discovery still expects `repo/repox/rulesets`.
- Registry and pack consumers still expect old `data/` and `packs/` paths.
- Import fallout remains in deeper test/tool lanes.
- Frozen contract hashes and generated evidence require reviewed refresh or
  explicit historical preservation.
- Some old source path expectations remain.

## Next Task

`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`
