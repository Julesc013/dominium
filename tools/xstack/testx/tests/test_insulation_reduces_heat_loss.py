"""FAST test: THERM-3 insulation reduces ambient heat exchange."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_insulation_reduces_heat_loss"
TEST_TAGS = ["fast", "thermal", "cooling"]


def _configure_boundary(graph: dict, *, insulation_permille: int) -> dict:
    out = copy.deepcopy(graph)
    for node in list(out.get("nodes") or []):
        if str(node.get("node_id", "")).strip() != "node.therm.source":
            continue
        payload = dict(node.get("payload") or {})
        ext = dict(payload.get("extensions") or {})
        ext["boundary_to_ambient"] = True
        ext["ambient_coupling_coefficient"] = 500
        ext["insulation_factor_permille"] = int(max(0, insulation_permille))
        payload["extensions"] = ext
        node["payload"] = payload
    return out


def _exchange_for_source(result: dict) -> int:
    rows = [
        dict(row)
        for row in list(result.get("ambient_exchange_rows") or [])
        if isinstance(row, dict) and str(row.get("node_id", "")).strip() == "node.therm.source"
    ]
    if not rows:
        return 0
    return int(max(0, int(rows[0].get("heat_exchange", 0))))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    base_graph = build_thermal_graph(source_energy=8000, sink_energy=200, conductance_value=0)
    exposed = solve_thermal_network_t1(
        graph_row=_configure_boundary(base_graph, insulation_permille=1000),
        current_tick=340,
        ambient_temperature=5,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    insulated = solve_thermal_network_t1(
        graph_row=_configure_boundary(base_graph, insulation_permille=250),
        current_tick=340,
        ambient_temperature=5,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    exposed_exchange = _exchange_for_source(exposed)
    insulated_exchange = _exchange_for_source(insulated)
    if exposed_exchange <= 0:
        return {"status": "fail", "message": "expected non-zero exposed ambient exchange"}
    if insulated_exchange >= exposed_exchange:
        return {"status": "fail", "message": "insulation should reduce ambient heat exchange"}
    return {"status": "pass", "message": "insulation lowers ambient heat transfer"}

