"""FAST test: MAT-10 stress run stays within per-tick cost envelopes via degradation."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.cost_usage_bounded_per_tick"
TEST_TAGS = ["fast", "materials", "mat10", "stress", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.mat_scale_testlib import (
        base_scenario,
        run_report,
        with_budget,
    )

    scenario = with_budget(
        base_scenario(seed=703, factory_complex_count=20, logistics_node_count=96, active_project_count=72, player_count=48),
        max_solver_cost_units_per_tick=5_000,
        max_inspection_cost_units_per_tick=480,
        max_micro_parts_per_roi=96,
    )
    report = run_report(scenario=scenario, tick_count=20)
    if not bool(report.get("bounded", False)):
        return {"status": "fail", "message": "stress report is not bounded under envelope"}
    for row in list(report.get("per_tick_reports") or []):
        if not isinstance(row, dict):
            continue
        cost_usage = dict(row.get("cost_usage") or {})
        if int(cost_usage.get("solver_cost_units", 0) or 0) > 5_000:
            return {"status": "fail", "message": "solver cost exceeded envelope without deterministic bounding"}
        if int(cost_usage.get("inspection_cost_units", 0) or 0) > 480:
            return {"status": "fail", "message": "inspection cost exceeded envelope without deterministic bounding"}
    return {"status": "pass", "message": "per-tick cost usage bounded passed"}
