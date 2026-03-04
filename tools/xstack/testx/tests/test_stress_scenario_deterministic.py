"""FAST test: FLUID stress scenario generation is deterministic for equivalent inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_fluid_stress_scenario_deterministic"
TEST_TAGS = ["fast", "fluid", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.fluid.tool_generate_fluid_stress import generate_fluid_stress_scenario

    a = generate_fluid_stress_scenario(
        seed=9701,
        tanks=8,
        vessels=3,
        pipes=36,
        pumps=3,
        valves=4,
        graphs=2,
        ticks=18,
        interior_compartment_count=6,
    )
    b = generate_fluid_stress_scenario(
        seed=9701,
        tanks=8,
        vessels=3,
        pipes=36,
        pumps=3,
        valves=4,
        graphs=2,
        ticks=18,
        interior_compartment_count=6,
    )
    if a != b:
        return {"status": "fail", "message": "FLUID stress scenario drifted across equivalent generation inputs"}
    if str(a.get("deterministic_fingerprint", "")).strip() != str(b.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "scenario deterministic_fingerprint mismatch"}
    return {"status": "pass", "message": "FLUID stress scenario generation deterministic"}
