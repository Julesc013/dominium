# MOVE-ROUTER-02 Status

Status: PARTIAL
Task: MOVE-ROUTER-02 - Repair References, Imports, Build, Projection, and Exceptions After Routing
Generated: 2026-05-18

## Summary

MOVE-ROUTER-02 repaired the first post-routing path and import layer after
MOVE-ROUTER-01 emptied the former bad roots.

- Starting HEAD: `2f722d626a316e3e1f827fd06a131b2a74e5f3d7`.
- `origin/main` at start: `2f722d626a316e3e1f827fd06a131b2a74e5f3d7`.
- Bad-root tracked file count after repair: 0.
- Active exact-path replacements recorded: 33,316.
- Files changed by exact path repair tooling: 1,171.
- Import replacements recorded: 76.
- Python files changed by import repair tooling: 74.
- Runtime control shim packages created: 3.
- CMake configure: PASS.
- CMake build: PARTIAL; compile and fast/smoke lanes passed, then broader TestX lanes failed.

## Result

The structural cleanup remains intact: no tracked files remain under the former
bad roots. The repository is not ready for final proof because active test,
RepoX, import, registry, frozen-hash, and stale-path surfaces still need a
second focused repair pass.

## Next Task

`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`
