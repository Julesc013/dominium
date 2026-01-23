# Boundary Enforcement

Dominium uses lightweight build-time guardrails to prevent layer leakage.

## Static Checks

- `scripts/verify_includes_sanity.py`:
  - Enforces include boundaries across engine/game/apps/tools.
- `scripts/verify_abi_boundaries.py`:
  - Blocks STL tokens in public headers.
- `tools/ci/arch_checks.py`:
  - Enforces repo layout and architecture rules (ARCH/DET/PERF/SCALE/EPIS).
- `cmake/BaselineHeaderCheck.cmake`:
  - Enforces C89/C++98 safety for baseline-visible public headers.
- `dom_assert_no_link(...)` (top-level CMake):
  - Blocks forbidden link dependencies (engine/game boundaries).

## CTest Coverage

These checks are wired into CLI-only tests:

- `build_include_sanity`
- `build_abi_boundaries`
- `build_arch_checks`

Run with:

```
ctest -R build_
```
