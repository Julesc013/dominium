"""FAST test: THERM-1 loss-to-heat inputs are applied to node thermal energy."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_loss_to_heat_applied"
TEST_TAGS = ["fast", "thermal", "integration"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph, heat_input_rows

    graph = build_thermal_graph(source_energy=500, sink_energy=0, conductance_value=0)
    baseline = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=21,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    heated = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=21,
        heat_input_rows=heat_input_rows(source_heat=250),
        max_processed_edges=64,
        max_cost_units=4096,
    )
    baseline_nodes = dict((str(r.get("node_id", "")), dict(r)) for r in list(baseline.get("node_status_rows") or []) if isinstance(r, dict))
    heated_nodes = dict((str(r.get("node_id", "")), dict(r)) for r in list(heated.get("node_status_rows") or []) if isinstance(r, dict))
    before = int(dict(baseline_nodes.get("node.therm.source") or {}).get("thermal_energy", 0))
    after = int(dict(heated_nodes.get("node.therm.source") or {}).get("thermal_energy", 0))
    if after <= before:
        return {"status": "fail", "message": "thermal energy did not increase after deterministic heat-loss input mapping"}
    return {"status": "pass", "message": "loss-to-heat mapping applied"}
