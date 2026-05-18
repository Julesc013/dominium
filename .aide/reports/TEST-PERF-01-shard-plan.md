Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# TEST-PERF-01 Shard Plan

| Lane | Command | Expected |
| --- | --- | --- |
| `focused-repox` | `ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300` | PASS |
| `smoke` | `ctest --preset verify -L smoke --output-on-failure --timeout 300` | PASS |
| `fast` | `ctest --preset verify -L fast --output-on-failure --timeout 300` | PASS |
| `audit` | `ctest --preset verify -L audit --output-on-failure --timeout 1200` | PASS slow |
| `tools-without-heavy-auditx` | `python scripts/test_tier.py --tier component-tools` | PASS |
| `slow` | `ctest --preset verify -L slow --output-on-failure --timeout 1200` | PASS slow |
| `nightly` | `ctest --preset verify -L nightly --output-on-failure --timeout 1200` | PASS slow |
| `semantic-lints` | `ctest --preset verify -R "slice0_hardcoded_ids|slice1_hardcoded_constants" --output-on-failure` | FAIL until semantic lint repair |
| `full-promotion` | `ctest --preset verify --output-on-failure` | FAIL until semantic lint repair |

Timeouts: smoke/fast use 300 seconds; AuditX slow/nightly uses 1200 seconds. Full promotion is unfiltered and remains blocked by semantic lints, not by AuditX wall-time.
