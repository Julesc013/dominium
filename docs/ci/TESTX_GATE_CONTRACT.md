Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# TestX Gate Contract

This document defines the operational gate for a “full TestX pass”.

## Canonical command

From the build tree (example: `out/build/vs2026/verify`):

```
cmake --build <build-dir> --config <cfg> --target testx_all
```

The `testx_all` target runs:

```
ctest --output-on-failure --timeout <DOM_TESTX_TIMEOUT> -C <cfg>
```

## Timeout policy

- `DOM_TESTX_TIMEOUT` is a **per-test** timeout in seconds.
- Default: `1200` (20 minutes).
- Override at configure time:
  - `-DDOM_TESTX_TIMEOUT=1200`

## Full pass definition

A full pass requires:
- `testx_all` completes with exit code 0.
- No failing or skipped tests.
- All determinism and schema tests are included in the run.

## Expected runtime bands (non-binding)

Local developer machines:
- Typical: 2–12 minutes
- Worst-case (debug + slow disks): up to 20 minutes

CI:
- Typical: 6–18 minutes
- Worst-case: up to 25 minutes

If runtime exceeds the default timeout, raise `DOM_TESTX_TIMEOUT` explicitly
and report the observed duration.
