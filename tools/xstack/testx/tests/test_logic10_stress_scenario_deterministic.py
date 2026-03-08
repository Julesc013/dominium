"""STRICT test: LOGIC-10 stress scenario generation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_stress_scenario_deterministic"
TEST_TAGS = ["strict", "logic", "envelope", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.logic.logic10_stress_common import generate_logic_stress_scenario

    first = generate_logic_stress_scenario(
        repo_root=repo_root,
        seed=1010,
        tick_count=8,
        network_count=12,
        mega_node_count=1_000_000,
    )
    second = generate_logic_stress_scenario(
        repo_root=repo_root,
        seed=1010,
        tick_count=8,
        network_count=12,
        mega_node_count=1_000_000,
    )
    for key in ("deterministic_fingerprint", "scenario_id", "expected_invariant_summary"):
        if first.get(key) != second.get(key):
            return {"status": "fail", "message": "logic stress scenario drifted for '{}'".format(key)}
    if dict(first.get("mega_network") or {}) != dict(second.get("mega_network") or {}):
        return {"status": "fail", "message": "logic mega-network descriptor drifted across equivalent generation runs"}
    if dict(first.get("distributed_control") or {}) != dict(second.get("distributed_control") or {}):
        return {"status": "fail", "message": "logic distributed-control descriptor drifted across equivalent generation runs"}
    return {"status": "pass", "message": "logic stress scenario generation is deterministic"}
