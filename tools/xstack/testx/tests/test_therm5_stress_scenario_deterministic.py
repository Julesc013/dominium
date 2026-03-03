"""FAST test: THERM-5 stress scenario generation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_stress_scenario_deterministic"
TEST_TAGS = ["fast", "thermal", "therm5", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.thermal.tool_generate_therm_stress_scenario import generate_therm_stress_scenario

    one = generate_therm_stress_scenario(
        seed=7801,
        node_count=96,
        link_count=180,
        radiator_count=24,
        graph_count=2,
        tick_horizon=24,
        include_fire_ignitions=True,
    )
    two = generate_therm_stress_scenario(
        seed=7801,
        node_count=96,
        link_count=180,
        radiator_count=24,
        graph_count=2,
        tick_horizon=24,
        include_fire_ignitions=True,
    )
    if dict(one) != dict(two):
        return {"status": "fail", "message": "THERM-5 stress scenario generation diverged for identical seed/inputs"}
    return {"status": "pass", "message": "THERM-5 stress scenario generation deterministic"}
