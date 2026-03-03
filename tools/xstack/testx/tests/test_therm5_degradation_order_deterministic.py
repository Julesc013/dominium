"""FAST test: THERM-5 degradation policy order is deterministic under budget pressure."""

from __future__ import annotations

import sys


TEST_ID = "test_degradation_order_deterministic"
TEST_TAGS = ["fast", "thermal", "therm5", "degradation", "determinism"]


_EXPECTED_ORDER = [
    "degrade.therm.tick_bucket",
    "degrade.therm.t0_budget",
    "degrade.therm.defer_noncritical_models",
    "degrade.therm.fire_spread_cap",
]


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.thermal.tool_generate_therm_stress_scenario import generate_therm_stress_scenario
    from tools.thermal.tool_run_therm_stress import run_therm_stress_scenario

    scenario = generate_therm_stress_scenario(
        seed=7802,
        node_count=128,
        link_count=240,
        radiator_count=16,
        graph_count=3,
        tick_horizon=16,
        include_fire_ignitions=True,
    )
    return run_therm_stress_scenario(
        scenario=scenario,
        tick_count=16,
        budget_envelope_id="therm.envelope.tight",
        max_cost_units_per_tick=700,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=220,
        base_t1_tick_stride=2,
        max_fire_spread_per_tick=12,
        ambient_temperature=20,
    )


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "THERM-5 stress fixture refused while validating degradation order"}

    first_order = list((dict(first.get("metrics") or {}).get("degradation_policy_order") or []))
    second_order = list((dict(second.get("metrics") or {}).get("degradation_policy_order") or []))
    if first_order != _EXPECTED_ORDER:
        return {"status": "fail", "message": "unexpected THERM degradation policy order"}
    if second_order != _EXPECTED_ORDER:
        return {"status": "fail", "message": "second run degraded policy order mismatch"}
    if first_order != second_order:
        return {"status": "fail", "message": "degradation policy order drifted across identical runs"}

    first_hash = str((dict(first.get("metrics") or {}).get("proof_hash_summary") or {}).get("degradation_event_hash_chain", "")).strip()
    second_hash = str((dict(second.get("metrics") or {}).get("proof_hash_summary") or {}).get("degradation_event_hash_chain", "")).strip()
    if first_hash != second_hash or len(first_hash) != 64:
        return {"status": "fail", "message": "degradation hash chain unstable or invalid"}

    return {"status": "pass", "message": "THERM-5 degradation order deterministic"}
