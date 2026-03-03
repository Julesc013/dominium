"""FAST test: THERM-5 replay-window verification matches baseline hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_window_hash_match"
TEST_TAGS = ["fast", "thermal", "therm5", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.thermal.tool_generate_therm_stress_scenario import generate_therm_stress_scenario
    from tools.thermal.tool_replay_therm_window import verify_therm_replay_window
    from tools.thermal.tool_run_therm_stress import run_therm_stress_scenario

    scenario = generate_therm_stress_scenario(
        seed=7804,
        node_count=120,
        link_count=220,
        radiator_count=24,
        graph_count=2,
        tick_horizon=20,
        include_fire_ignitions=True,
    )
    baseline = run_therm_stress_scenario(
        scenario=scenario,
        tick_count=20,
        budget_envelope_id="therm.envelope.standard",
        max_cost_units_per_tick=1800,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=520,
        base_t1_tick_stride=1,
        max_fire_spread_per_tick=24,
        ambient_temperature=20,
    )
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline THERM stress run failed for replay fixture"}

    replay = verify_therm_replay_window(
        scenario=scenario,
        baseline_report=baseline,
        tick_start=0,
        tick_end=10,
        budget_envelope_id="therm.envelope.standard",
        max_cost_units_per_tick=1800,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=520,
        base_t1_tick_stride=1,
        max_fire_spread_per_tick=24,
        ambient_temperature=20,
    )
    if str(replay.get("result", "")) != "complete":
        return {"status": "fail", "message": "THERM replay-window verification failed"}
    matches = dict(replay.get("matches") or {})
    required = (
        "proof_window_match",
        "temperature_window_match",
        "event_window_match",
        "degradation_window_match",
        "full_proof_summary_match",
    )
    for key in required:
        if not bool(matches.get(key, False)):
            return {"status": "fail", "message": "replay-window mismatch for '{}'".format(key)}
    return {"status": "pass", "message": "THERM-5 replay window hash verification stable"}
