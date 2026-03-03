"""FAST test: line resistance proxy applies deterministic active-power loss."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_line_loss_applied"
TEST_TAGS = ["fast", "electric", "loss"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.electric.power_network_engine import solve_power_network_e1
    from tools.xstack.testx.tests.elec_testlib import build_power_graph, model_binding_rows

    graph_row = build_power_graph(capacity_rating=100, resistance_proxy=40)
    bindings = model_binding_rows(resistive_demand_p=100, motor_demand_p=0, motor_pf_permille=1000)
    solved = solve_power_network_e1(
        graph_row=copy.deepcopy(graph_row),
        model_binding_rows=copy.deepcopy(bindings),
        current_tick=33,
        max_processed_edges=32,
    )
    edge_rows = [dict(row) for row in list(solved.get("edge_status_rows") or []) if isinstance(row, dict)]
    if len(edge_rows) != 1:
        return {"status": "fail", "message": "expected one edge status row for one-edge fixture"}
    edge = dict(edge_rows[0])
    delivered_p = int(edge.get("P", -1))
    heat_loss = int(edge.get("heat_loss_stub", -1))
    if heat_loss <= 0:
        return {"status": "fail", "message": "line loss proxy should emit positive heat_loss_stub for resistive edge"}
    if delivered_p >= 100:
        return {"status": "fail", "message": "delivered active power should be reduced by loss proxy"}
    return {"status": "pass", "message": "line loss proxy applied deterministically"}

