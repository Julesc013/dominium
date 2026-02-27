"""FAST test: MAT-10 stress inspection cache reuses snapshots and avoids thrash."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.inspection_cache_prevents_thrashing"
TEST_TAGS = ["fast", "materials", "mat10", "inspection", "cache"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.mat_scale_testlib import (
        base_scenario,
        run_report,
        with_workload_overrides,
    )

    scenario = with_workload_overrides(
        base_scenario(seed=719, factory_complex_count=12, logistics_node_count=48, active_project_count=24, player_count=32),
        {
            "truth_anchor_interval_ticks": 32,
            "inspection_desired_fidelity": "meso",
            "inspection_history_window_ticks": 4,
        },
    )
    report = run_report(scenario=scenario, tick_count=24)
    summary = dict(report.get("inspection_cache_summary") or {})
    hits = int(summary.get("hits", 0) or 0)
    misses = int(summary.get("misses", 0) or 0)
    if hits <= 0:
        return {"status": "fail", "message": "inspection cache produced no hits under repeated queries"}
    if hits <= misses // 10:
        return {"status": "fail", "message": "inspection cache hit ratio too low for deterministic reuse"}
    return {"status": "pass", "message": "inspection cache thrash prevention passed"}
