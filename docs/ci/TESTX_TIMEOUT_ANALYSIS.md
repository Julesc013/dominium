Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# TestX Timeout Analysis

## Current CTest timeout surfaces

- `verify_fast` in `CMakeLists.txt` passes `--timeout ${DOM_VERIFY_FAST_TIMEOUT}` when running `smoke`, `portability`, and `buildmeta` labels.
- `DOM_VERIFY_FAST_TIMEOUT` defaults to **300 seconds**.
- Heavy AuditX scan coverage is classified under the `auditx` label instead of the 300-second portability lane.
- `tools_auditx`, `tools_auditx_hash_stability`, and `tools_auditx_changed_only` have explicit CTest `TIMEOUT` properties of **1200 seconds**.
- AuditX CTest outputs are routed to `.dominium.local/ctest/auditx/` instead of mutating tracked canonical audit artifacts.

## TestX target behavior

`testx_all` is currently manifest-driven through `scripts/dev/testx_proof_engine.py`. It selects CTest tests from `data/registries/testx_suites.json` and invokes CTest for the selected suite.

## Determinism implications

- Timeout values are static CMake/test metadata.
- The AuditX shard is selected by stable CTest labels and test names.
- No dynamic or machine-dependent timeout calculation is used.

## Override procedure

To override the fast-lane per-test timeout at configure time:

```
cmake -DDOM_VERIFY_FAST_TIMEOUT=300 -S <src> -B <build>
```

This changes timeout behavior only and does not alter test selection.
