"""FAST test: deterministic ELEC-1 E1 solve produces stable power flow outputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_power_flow_deterministic"
TEST_TAGS = ["fast", "electric", "flow", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.electric.power_network_engine import solve_power_network_e1
    from tools.xstack.testx.tests.elec_testlib import build_power_graph, model_binding_rows

    graph_row = build_power_graph(capacity_rating=320, resistance_proxy=12)
    bindings = model_binding_rows(resistive_demand_p=120, motor_demand_p=60, motor_pf_permille=830)
    first = solve_power_network_e1(
        graph_row=copy.deepcopy(graph_row),
        model_binding_rows=copy.deepcopy(bindings),
        current_tick=12,
        max_processed_edges=32,
    )
    second = solve_power_network_e1(
        graph_row=copy.deepcopy(graph_row),
        model_binding_rows=copy.deepcopy(bindings),
        current_tick=12,
        max_processed_edges=32,
    )
    if first != second:
        return {"status": "fail", "message": "E1 power flow solve diverged for equivalent deterministic inputs"}
    if str(first.get("mode", "")) != "E1":
        return {"status": "fail", "message": "expected E1 mode solve result"}
    rows = [dict(row) for row in list(first.get("flow_channels") or []) if isinstance(row, dict)]
    if not rows:
        return {"status": "fail", "message": "E1 solve emitted no flow channels"}
    for row in rows:
        if str(row.get("quantity_bundle_id", "")).strip() != "bundle.power_phasor":
            return {"status": "fail", "message": "power channels must use bundle.power_phasor"}
    return {"status": "pass", "message": "E1 power flow deterministic"}

