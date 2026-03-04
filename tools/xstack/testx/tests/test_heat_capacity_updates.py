"""FAST test: THERM-1 heat-capacity model updates node temperature deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_heat_capacity_updates"
TEST_TAGS = ["fast", "thermal", "models"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = build_thermal_graph(source_energy=1000, sink_energy=0, source_capacity=100, sink_capacity=100)
    solved = solve_thermal_network_t1(
        graph_row=graph,
        current_tick=10,
        max_processed_edges=64,
        max_cost_units=4096,
        ambient_temperature=20,
    )
    nodes = dict(
        (str(row.get("node_id", "")).strip(), dict(row))
        for row in list(solved.get("node_status_rows") or [])
        if isinstance(row, dict)
    )
    source = dict(nodes.get("node.therm.source") or {})
    if not source:
        return {"status": "fail", "message": "source node missing from thermal solve output"}
    expected_temp = 20 + (int(source.get("thermal_energy", 0)) // 100)
    actual_temp = int(source.get("temperature", -1))
    if actual_temp != expected_temp:
        return {
            "status": "fail",
            "message": "heat-capacity mapping mismatch: expected {}, got {}".format(expected_temp, actual_temp),
        }
    return {"status": "pass", "message": "heat-capacity update deterministic"}
