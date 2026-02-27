"""FAST test: MAT-10 degradation order follows deterministic policy sequence."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.degradation_order_deterministic"
TEST_TAGS = ["fast", "materials", "mat10", "stress", "degradation"]


def _unique_in_order(values):
    out = []
    seen = set()
    for token in values:
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.materials.performance.mat_scale_engine import DEFAULT_MAT_DEGRADATION_ORDER
    from tools.xstack.testx.tests.mat_scale_testlib import (
        base_scenario,
        run_report,
        with_budget,
        with_workload_overrides,
    )

    scenario = base_scenario(
        seed=709,
        factory_complex_count=8,
        logistics_node_count=32,
        active_project_count=32,
        player_count=24,
    )
    scenario = with_workload_overrides(
        scenario,
        {
            "materialization_micro_parts_per_player": 1024,
            "construction_parallel_steps": 16,
            "construction_active_steps": 32,
            "logistics_manifests_per_tick": 120,
            "logistics_route_lookups_per_tick": 120,
            "maintenance_low_priority_due_per_tick": 120,
            "inspection_desired_fidelity": "micro",
        },
    )
    scenario = with_budget(
        scenario,
        max_solver_cost_units_per_tick=500,
        max_inspection_cost_units_per_tick=40,
        max_micro_parts_per_roi=64,
    )
    report = run_report(scenario=scenario, tick_count=2)
    steps = [
        str(row.get("step_id", "")).strip()
        for row in list(report.get("degradation_events") or [])
        if isinstance(row, dict)
    ]
    if not steps:
        return {"status": "fail", "message": "expected degradation events under constrained envelope"}
    unique_steps = _unique_in_order(steps)
    expected = list(DEFAULT_MAT_DEGRADATION_ORDER)
    prefix = expected[: len(unique_steps)]
    if unique_steps != prefix:
        return {
            "status": "fail",
            "message": "degradation order drifted: got={} expected_prefix={}".format(unique_steps, prefix),
        }
    return {"status": "pass", "message": "degradation order deterministic passed"}
