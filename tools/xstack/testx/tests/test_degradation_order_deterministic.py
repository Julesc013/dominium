"""FAST test: FLUID degradation order is deterministic and follows required sequence."""

from __future__ import annotations

import sys


TEST_ID = "test_fluid_degradation_order_deterministic"
TEST_TAGS = ["fast", "fluid", "degradation", "determinism"]


def _is_non_decreasing(values):
    return list(values) == sorted(values)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.fluid.tool_generate_fluid_stress import generate_fluid_stress_scenario
    from tools.fluid.tool_run_fluid_stress import run_fluid_stress_scenario

    scenario = generate_fluid_stress_scenario(
        seed=9702,
        tanks=10,
        vessels=4,
        pipes=48,
        pumps=4,
        valves=5,
        graphs=2,
        ticks=20,
        interior_compartment_count=6,
    )
    first = run_fluid_stress_scenario(
        scenario=scenario,
        tick_count=20,
        budget_envelope_id="fluid.envelope.tight",
        max_cost_units_per_tick=900,
        max_processed_edges_per_network=256,
        max_model_cost_units_per_network=220,
        base_f1_tick_stride=2,
        max_failure_events_per_tick=16,
        base_max_leak_evaluations_per_tick=10,
    )
    second = run_fluid_stress_scenario(
        scenario=scenario,
        tick_count=20,
        budget_envelope_id="fluid.envelope.tight",
        max_cost_units_per_tick=900,
        max_processed_edges_per_network=256,
        max_model_cost_units_per_network=220,
        base_f1_tick_stride=2,
        max_failure_events_per_tick=16,
        base_max_leak_evaluations_per_tick=10,
    )
    rows_a = [dict(row) for row in list(dict(first.get("extensions") or {}).get("fluid_degradation_event_rows") or []) if isinstance(row, dict)]
    rows_b = [dict(row) for row in list(dict(second.get("extensions") or {}).get("fluid_degradation_event_rows") or []) if isinstance(row, dict)]
    if not rows_a:
        return {"status": "fail", "message": "expected deterministic degradation rows under tight envelope"}
    if rows_a != rows_b:
        return {"status": "fail", "message": "degradation rows drifted across equivalent runs"}
    by_scope = {}
    for row in rows_a:
        scope = "{}::{}".format(int(row.get("tick", 0) or 0), str(row.get("graph_id", "")))
        by_scope.setdefault(scope, [])
        by_scope[scope].append(int(row.get("step_order", 999) or 999))
    for values in by_scope.values():
        if not _is_non_decreasing(values):
            return {"status": "fail", "message": "degradation step_order is not non-decreasing per tick/graph scope"}
    assertions = dict(first.get("assertions") or {})
    if not bool(assertions.get("degradation_order_deterministic", False)):
        return {"status": "fail", "message": "harness did not report deterministic degradation order"}
    return {"status": "pass", "message": "FLUID degradation order deterministic and ordered"}
