Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: TEST-PERF-01

# CTest Sharding And AuditX Wall-Time Baseline

## Result

`tools_auditx` was a cold full AuditX scan inside the 300-second portability lane. It timed out at 300.195 seconds with CTest return code 8.

AuditX scan coverage is now a dedicated CTest shard:

- `tools_auditx`
- `tools_auditx_hash_stability`
- `tools_auditx_changed_only`

All three tests carry the `auditx` label and a 1200-second CTest timeout. They write under `.dominium.local/ctest/auditx/` so CTest does not mutate tracked canonical AuditX artifacts.

## Timing

| Lane | Test | Seconds | Result |
| --- | --- | ---: | --- |
| baseline 300s | `tools_auditx` | 300.195 | FAIL timeout |
| auditx shard | `tools_auditx` | 823.085 | PASS |
| auditx shard | `tools_auditx_hash_stability` | 13.638 | PASS |
| auditx shard | `tools_auditx_changed_only` | 8.334 | PASS |

## Commands

```text
py -3 scripts/test_timing_report.py --preset verify --config Debug --regex tools_auditx --limit 1 --timeout 300 --out .dominium.local/test-perf-01/tools-auditx-ctest-timeout300.json --md-out .dominium.local/test-perf-01/tools-auditx-ctest-timeout300.md
py -3 scripts/test_timing_report.py --preset verify --config Debug --label-regex auditx --limit 3 --timeout 1200 --out .dominium.local/test-perf-01/auditx-shard-timeout1200.json --md-out .dominium.local/test-perf-01/auditx-shard-timeout1200.md
```

## Disposition

This does not weaken AuditX. The heavy scan remains in full CTest and is explicitly runnable with:

```text
ctest --preset verify -L auditx --timeout 1200 --output-on-failure
```

The 300-second fast lane is reserved for smoke, portability, and buildmeta tests that can reasonably complete inside that bound.
