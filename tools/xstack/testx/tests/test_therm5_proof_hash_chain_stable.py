"""FAST test: THERM-5 proof hash chains are stable for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_proof_hash_chain_stable"
TEST_TAGS = ["fast", "thermal", "therm5", "proof", "determinism"]


def _proof_summary(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.thermal.tool_generate_therm_stress_scenario import generate_therm_stress_scenario
    from tools.thermal.tool_run_therm_stress import run_therm_stress_scenario

    scenario = generate_therm_stress_scenario(
        seed=7803,
        node_count=110,
        link_count=200,
        radiator_count=20,
        graph_count=2,
        tick_horizon=18,
        include_fire_ignitions=True,
    )
    report = run_therm_stress_scenario(
        scenario=scenario,
        tick_count=18,
        budget_envelope_id="therm.envelope.standard",
        max_cost_units_per_tick=1800,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=520,
        base_t1_tick_stride=1,
        max_fire_spread_per_tick=24,
        ambient_temperature=20,
    )
    return dict((dict(report.get("metrics") or {}).get("proof_hash_summary") or {}))


def run(repo_root: str):
    first = _proof_summary(repo_root)
    second = _proof_summary(repo_root)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "THERM-5 proof hash summary drifted across identical runs"}

    for key in (
        "thermal_network_state_hash_chain",
        "heat_input_hash_chain",
        "overtemp_trip_hash_chain",
        "fire_cascade_hash_chain",
        "degradation_event_hash_chain",
        "proof_hash_summary",
    ):
        value = str(first.get(key, "")).strip()
        if len(value) != 64:
            return {"status": "fail", "message": "proof hash field '{}' missing or invalid".format(key)}

    return {"status": "pass", "message": "THERM-5 proof hash chains stable"}
