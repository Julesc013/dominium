"""FAST test: ELEC-5 replay-window verification matches baseline hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_window_hash_match"
TEST_TAGS = ["fast", "electric", "elec5", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.electric.tool_generate_elec_stress_scenario import generate_elec_stress_scenario
    from tools.electric.tool_replay_elec_window import verify_elec_replay_window
    from tools.electric.tool_run_elec_stress import run_elec_stress_scenario

    scenario = generate_elec_stress_scenario(
        seed=5601,
        generator_count=4,
        load_count=16,
        storage_count=2,
        breaker_count=6,
        graph_count=1,
        shard_count=2,
        tick_horizon=18,
    )
    baseline = run_elec_stress_scenario(
        scenario=scenario,
        tick_count=18,
        budget_envelope_id="elec.envelope.standard",
        max_network_solves_per_tick=4,
        max_edges_per_network=4096,
        max_fault_evals_per_tick=4096,
        max_trip_actions_per_tick=4096,
        cascade_max_iterations=4,
    )
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline stress run failed for replay-window fixture"}
    replay = verify_elec_replay_window(
        scenario=scenario,
        baseline_report=baseline,
        tick_start=0,
        tick_end=8,
        budget_envelope_id="elec.envelope.standard",
        max_network_solves_per_tick=4,
        max_edges_per_network=4096,
        max_fault_evals_per_tick=4096,
        max_trip_actions_per_tick=4096,
        cascade_max_iterations=4,
    )
    if str(replay.get("result", "")) != "complete":
        return {"status": "fail", "message": "replay-window verification failed"}
    matches = dict(replay.get("matches") or {})
    if (not bool(matches.get("window_hashes_match", False))) or (not bool(matches.get("full_proof_summary_match", False))):
        return {"status": "fail", "message": "replay-window hash mismatch against baseline report"}
    return {"status": "pass", "message": "ELEC-5 replay window hash verification stable"}

