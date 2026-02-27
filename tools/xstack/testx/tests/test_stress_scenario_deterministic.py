"""FAST test: MAT-10 stress scenario generation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.stress_scenario_deterministic"
TEST_TAGS = ["fast", "materials", "mat10", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.materials.performance.mat_scale_engine import default_factory_planet_scenario

    one = default_factory_planet_scenario(
        seed=701,
        factory_complex_count=16,
        logistics_node_count=64,
        active_project_count=32,
        player_count=24,
    )
    two = default_factory_planet_scenario(
        seed=701,
        factory_complex_count=16,
        logistics_node_count=64,
        active_project_count=32,
        player_count=24,
    )
    if one != two:
        return {"status": "fail", "message": "factory-planet scenario generation diverged"}
    return {"status": "pass", "message": "stress scenario deterministic generation passed"}
