# MOVE-ROUTER-02 Build Proof

Status: PARTIAL
Generated: 2026-05-18

## Commands

- `cmake --preset verify`: PASS.
- `cmake --build --preset verify`: PARTIAL.

## Build Interpretation

The build advanced through configure, compilation, and the integrated fast/smoke
CTest set. The integrated 57-test fast/smoke group passed. The broader
portability/TestX phase then failed with 140 failures out of 344 tests.

## Remaining Failure Classes

- RepoX ruleset discovery still points at `repo/repox/rulesets`.
- Test/tool lanes still reference `data/registries`, `data/packs`, and `packs`.
- Some old import packages need canonical rewrites or narrow shims.
- Frozen hashes and generated evidence need reviewed disposition.
- Some tests still reference pre-router source paths.

No final build-green claim is made.
