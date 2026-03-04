"""FAST test: THERM-1 edge conduction is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_conduction_deterministic"
TEST_TAGS = ["fast", "thermal", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = build_thermal_graph(source_energy=4000, sink_energy=200, conductance_value=60)
    first = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=50,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    second = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=50,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "thermal T1 solve diverged for identical inputs"}
    if str(first.get("mode", "")) != "T1":
        return {"status": "fail", "message": "expected T1 mode solve"}
    edge_rows = [dict(row) for row in list(first.get("edge_status_rows") or []) if isinstance(row, dict)]
    if not edge_rows:
        return {"status": "fail", "message": "thermal solve produced no edge status rows"}
    transfer = int(max(int(edge_rows[0].get("heat_transfer", 0)), 0))
    if transfer <= 0:
        return {"status": "fail", "message": "conduction transfer should be positive for hot->cold edge"}
    return {"status": "pass", "message": "thermal conduction deterministic"}
