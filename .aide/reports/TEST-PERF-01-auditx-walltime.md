Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# TEST-PERF-01 AuditX Wall-Time

`tools_auditx` exceeds a 300-second fast-lane budget because it performs a cold full AuditX semantic scan and validates generated canonical artifact shape. It is bounded, but slow.

## Current Shard

| Test | Seconds | Result |
| --- | ---: | --- |
| `tools_auditx` | 798.97 | PASS |
| `tools_auditx_hash_stability` | 15.95 | PASS |
| `tools_auditx_changed_only` | 9.47 | PASS |

Shard total: 824.573 seconds.

## Classification

- Cause: broad full semantic scan and artifact validation, not a hang.
- Action: keep mandatory AuditX coverage in explicit `audit`/`auditx`/`slow`/`nightly` labels.
- Timeout: 1200 seconds for AuditX shard tests.
- Fast-lane status: excluded from 300-second smoke/fast feedback by label, not skipped from full proof.

## Rerun

```powershell
ctest --preset verify -L audit --output-on-failure --timeout 1200
```
