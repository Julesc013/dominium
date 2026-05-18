Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: TEST-PERF-01

# TEST-PERF-01 CTest Sharding Audit

## Status

Result: PASS_WITH_WARNINGS.

TEST-PERF-01 makes the post-restructure CTest state measurable and shardable without deleting tests, weakening assertions, or hiding known failures.

## Scope

This task covered CTest labels, shard commands, timing evidence, and the `tools_auditx` wall-time lane. It did not move roots, repair semantic lint findings, change runtime behavior, publish releases, or mark full CTest green.

## CTest Inventory

- Preset: `verify`.
- Total tests discovered: 495.
- Smoke tests: 57.
- Fast-label tests: 57.
- Audit/AuditX tests: 3.
- Slow/nightly tests: 3.
- Focused RepoX test: `inv_repox_rules`.

Structured inventory: `.aide/reports/TEST-PERF-01-ctest-inventory.json`.

## Timing Baseline

| Lane | Result | Seconds |
| --- | --- | ---: |
| `focused_repox` | PASS | 128.978 |
| `smoke` | PASS | 55.829 |
| `fast` | PASS | 48.821 |
| `slice0_hardcoded_ids` | FAIL | 9.943 |
| `slice1_hardcoded_constants` | FAIL | 2.871 |
| `auditx_shard` | PASS | 824.573 |

Structured timing: `.aide/reports/TEST-PERF-01-ctest-timing.json`.

## AuditX Wall-Time

`tools_auditx` is a cold full AuditX artifact scan. It is bounded and passes as a slow shard, but it is not a 300-second fast-lane test.

The current AuditX shard is:

- `tools_auditx`: 798.97 seconds in the measured shard run.
- `tools_auditx_hash_stability`: 15.95 seconds.
- `tools_auditx_changed_only`: 9.47 seconds.

This confirms the earlier 300-second timeout was a wall-time classification problem, not proof that AuditX should be weakened.

## Changes Applied

- Added a `fast` CTest label to existing `smoke` TestX tests.
- Added `audit`, `slow`, and `nightly` labels to the existing AuditX CTest shard while retaining the `auditx` compatibility label.
- Preserved the 1200-second timeout on the three AuditX shard tests.
- Added an impact-graph fallback so dirty changed paths that do not match a registered TestX/AuditX group still select core TestX/AuditX groups instead of collapsing FULL impacted planning to non-sharded runners.

## Commands

```powershell
ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300
ctest --preset verify -L smoke --output-on-failure --timeout 300
ctest --preset verify -L fast --output-on-failure --timeout 300
python scripts/test_tier.py --tier component-tools
ctest --preset verify -L audit --output-on-failure --timeout 1200
ctest --preset verify -L slow --output-on-failure --timeout 1200
ctest --preset verify -L nightly --output-on-failure --timeout 1200
ctest --preset verify -R "slice0_hardcoded_ids|slice1_hardcoded_constants" --output-on-failure
ctest --preset verify --output-on-failure
```

## Remaining Blockers

- `slice0_hardcoded_ids` remains a semantic lint blocker.
- `slice1_hardcoded_constants` remains a semantic lint blocker.
- Full unfiltered CTest remains not green until those semantic lint lanes are repaired.

Next task: `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS - Hardcoded Identifier and Constant Disposition`.
