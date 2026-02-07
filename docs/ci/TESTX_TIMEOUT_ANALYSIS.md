Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# TestX Timeout Analysis

## Source of timeout enforcement

- **Definition location:** `CMakeLists.txt` (testx_all target)
- **Mechanism:** CTest `--timeout` argument
- **Variable:** `DOM_TESTX_TIMEOUT` (CMake cache string)
- **Scope:** **Per-test** timeout (CTest semantics), not a global suite timeout

## Current value

- `DOM_TESTX_TIMEOUT`: **1200 seconds** (20 minutes)

## Command path (as configured)

From CMake:

- `set(DOM_TESTX_TIMEOUT "1200" CACHE STRING "Per-test timeout seconds for TestX gate")`
- `set(_dom_testx_ctest_cmd ${CMAKE_CTEST_COMMAND} --output-on-failure)`
- `list(APPEND _dom_testx_ctest_cmd --timeout ${DOM_TESTX_TIMEOUT})`
- `add_custom_target(testx_all COMMAND ${_dom_testx_ctest_cmd} ...)`

## Determinism implications

- Timeout is deterministic at the per-test level.
- No dynamic or machine-dependent timeouts are used in the TestX gate.

## Override procedure

To override the per-test timeout at configure time:

```
cmake -DDOM_TESTX_TIMEOUT=1200 -S <src> -B <build>
```

This changes the per-test timeout only and does not alter test selection.
