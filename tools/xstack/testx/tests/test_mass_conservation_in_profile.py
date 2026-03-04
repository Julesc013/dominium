"""FAST test: FLUID stress profile run reports no silent mass mutation."""

from __future__ import annotations

import sys


TEST_ID = "test_mass_conservation_in_profile"
TEST_TAGS = ["fast", "fluid", "conservation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.fluid.tool_generate_fluid_stress import generate_fluid_stress_scenario
    from tools.fluid.tool_run_fluid_stress import run_fluid_stress_scenario

    scenario = generate_fluid_stress_scenario(
        seed=9705,
        tanks=6,
        vessels=2,
        pipes=28,
        pumps=2,
        valves=3,
        graphs=1,
        ticks=16,
        interior_compartment_count=4,
    )
    report = run_fluid_stress_scenario(
        scenario=scenario,
        tick_count=16,
        budget_envelope_id="fluid.envelope.standard",
        max_cost_units_per_tick=2200,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=760,
        base_f1_tick_stride=1,
        max_failure_events_per_tick=64,
        base_max_leak_evaluations_per_tick=64,
    )
    assertions = dict(report.get("assertions") or {})
    if not bool(assertions.get("no_silent_mass_changes", False)):
        return {"status": "fail", "message": "FLUID stress report flagged silent mass mutation"}
    if not bool(assertions.get("all_failures_logged", False)):
        return {"status": "fail", "message": "FLUID stress report flagged unlogged failures"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "FLUID stress report refused under conservation fixture"}
    return {"status": "pass", "message": "FLUID stress profile reports explicit mass/failure accounting"}
