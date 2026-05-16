Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# TEST-PERF-00 CTest Tiers

The tier authority for local validation selection is `tests/validation_tiers.json`.

| Tier | Use |
| --- | --- |
| `t0` | fast AIDE and repo sanity validation |
| `ctest-smoke` | configured canonical CTest smoke subset |
| `focused-repox` | reproduce `inv_repox_rules` without running full CTest |
| `component-contracts` | contract/schema/invariant/registry work |
| `component-distribution` | distribution and product-proof-adjacent work |
| `component-tools` | tooling and governance tool work |
| `component-runtime` | runtime, integration, determinism, and platform work |
| `timing-sample` | bounded timing sample |
| `full-promotion` | full canonical CTest promotion gate |

Typical commands:

```text
python scripts/test_tier.py --list
python scripts/test_tier.py --tier t0
python scripts/test_impacted.py --from HEAD~1
python scripts/test_impacted.py --from HEAD~1 --include-worktree --run
python scripts/test_timing_report.py --preset verify --config Debug --regex invariant_units_present --limit 1 --out .dominium.local/test-perf-00/timing-sample.json
```

Full CTest remains available through:

```text
python scripts/test_tier.py --tier full-promotion
```
