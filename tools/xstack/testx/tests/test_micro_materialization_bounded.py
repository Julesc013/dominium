"""FAST test: MAT-10 stress keeps micro materialization within deterministic cap."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.micro_materialization_bounded"
TEST_TAGS = ["fast", "materials", "mat10", "materialization", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.mat_scale_testlib import (
        base_scenario,
        run_report,
        with_budget,
        with_workload_overrides,
    )

    scenario = base_scenario(seed=727, factory_complex_count=10, logistics_node_count=40, active_project_count=30, player_count=18)
    scenario = with_workload_overrides(
        scenario,
        {"materialization_micro_parts_per_player": 4096, "inspection_desired_fidelity": "micro"},
    )
    scenario = with_budget(
        scenario,
        max_solver_cost_units_per_tick=2_500,
        max_inspection_cost_units_per_tick=240,
        max_micro_parts_per_roi=72,
    )
    report = run_report(scenario=scenario, tick_count=12)
    for row in list(report.get("per_tick_reports") or []):
        if not isinstance(row, dict):
            continue
        workload = dict(row.get("workload") or {})
        if int(workload.get("materialization_micro_parts_per_player", 0) or 0) > 72:
            return {"status": "fail", "message": "micro materialization cap exceeded in workload"}
    return {"status": "pass", "message": "micro materialization bounded cap passed"}
