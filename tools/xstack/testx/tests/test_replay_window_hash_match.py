"""FAST test: FLUID replay-window verification matches baseline hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_fluid_replay_window_hash_match"
TEST_TAGS = ["fast", "fluid", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.fluid.tool_generate_fluid_stress import generate_fluid_stress_scenario
    from tools.fluid.tool_replay_fluid_window import verify_fluid_replay_window
    from tools.fluid.tool_run_fluid_stress import run_fluid_stress_scenario

    scenario = generate_fluid_stress_scenario(
        seed=9704,
        tanks=8,
        vessels=3,
        pipes=40,
        pumps=3,
        valves=4,
        graphs=2,
        ticks=20,
        interior_compartment_count=6,
    )
    baseline = run_fluid_stress_scenario(
        scenario=scenario,
        tick_count=20,
        budget_envelope_id="fluid.envelope.standard",
        max_cost_units_per_tick=2400,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=860,
        base_f1_tick_stride=1,
        max_failure_events_per_tick=64,
        base_max_leak_evaluations_per_tick=64,
    )
    if str(baseline.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "baseline FLUID stress run failed for replay fixture"}
    replay = verify_fluid_replay_window(
        scenario=scenario,
        baseline_report=baseline,
        tick_start=0,
        tick_end=10,
        budget_envelope_id="fluid.envelope.standard",
        max_cost_units_per_tick=2400,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=860,
        base_f1_tick_stride=1,
        max_failure_events_per_tick=64,
        base_max_leak_evaluations_per_tick=64,
    )
    if str(replay.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "FLUID replay-window verification failed"}
    matches = dict(replay.get("matches") or {})
    required = (
        "proof_window_match",
        "head_window_match",
        "event_window_match",
        "degradation_window_match",
        "full_proof_summary_match",
    )
    for key in required:
        if not bool(matches.get(key, False)):
            return {"status": "fail", "message": "replay-window mismatch for '{}'".format(key)}
    return {"status": "pass", "message": "FLUID replay window hash verification stable"}
