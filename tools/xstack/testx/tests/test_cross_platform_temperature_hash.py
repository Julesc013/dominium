"""STRICT test: THERM-1 temperature hash is stable across equivalent ordering variants."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_cross_platform_temperature_hash"
TEST_TAGS = ["strict", "thermal", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph_a = build_thermal_graph(source_energy=2750, sink_energy=100, conductance_value=35)
    graph_b = copy.deepcopy(graph_a)
    graph_b["nodes"] = list(reversed(list(graph_b.get("nodes") or [])))
    graph_b["edges"] = list(reversed(list(graph_b.get("edges") or [])))

    first = solve_thermal_network_t1(
        graph_row=graph_a,
        current_tick=88,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    second = solve_thermal_network_t1(
        graph_row=graph_b,
        current_tick=88,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    first_hash = str(first.get("thermal_network_hash", "")).strip().lower()
    second_hash = str(second.get("thermal_network_hash", "")).strip().lower()
    if (not first_hash) or (not second_hash):
        return {"status": "fail", "message": "thermal_network_hash missing from THERM-1 solve output"}
    if first_hash != second_hash:
        return {"status": "fail", "message": "thermal_network_hash changed for equivalent deterministic graph ordering"}
    return {"status": "pass", "message": "thermal hash stable across equivalent ordering variants"}
