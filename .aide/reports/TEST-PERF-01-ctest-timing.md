Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# TEST-PERF-01 CTest Timing

| Lane | Seconds | Result | Notes |
| --- | ---: | --- | --- |
| `focused_repox` | 128.978 | PASS | required_green |
| `smoke` | 55.829 | PASS | required_green |
| `fast` | 48.821 | PASS | required_green |
| `slice0_hardcoded_ids` | 9.943 | FAIL | known_semantic_lint |
| `slice1_hardcoded_constants` | 2.871 | FAIL | known_semantic_lint |
| `auditx_shard` | 824.573 | PASS | required_green_slow_shard |

Initial smoke and fast attempts failed on `test_gate_full_profile_shards_groups` before the impact-graph fallback was added. Final smoke and fast reruns pass.

Known semantic lint failures remain assigned to `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS`.
