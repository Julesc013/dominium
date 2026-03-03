"""FAST test: THERM-3 ambient exchange is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_ambient_exchange_deterministic"
TEST_TAGS = ["fast", "thermal", "determinism", "cooling"]


def _enable_ambient_boundary(graph: dict) -> dict:
    out = copy.deepcopy(graph)
    for node in list(out.get("nodes") or []):
        if str(node.get("node_id", "")).strip() != "node.therm.source":
            continue
        payload = dict(node.get("payload") or {})
        ext = dict(payload.get("extensions") or {})
        ext["boundary_to_ambient"] = True
        ext["ambient_coupling_coefficient"] = 500
        ext["insulation_factor_permille"] = 1000
        payload["extensions"] = ext
        node["payload"] = payload
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = _enable_ambient_boundary(
        build_thermal_graph(source_energy=7000, sink_energy=200, conductance_value=20)
    )
    first = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=200,
        ambient_temperature=15,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    second = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=200,
        ambient_temperature=15,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "ambient exchange solve diverged for identical inputs"}
    ambient_rows = [
        dict(row)
        for row in list(first.get("ambient_exchange_rows") or [])
        if isinstance(row, dict)
    ]
    if not ambient_rows:
        return {"status": "fail", "message": "expected ambient exchange rows for boundary node"}
    if not str(first.get("ambient_exchange_hash", "")).strip():
        return {"status": "fail", "message": "ambient exchange hash must be present"}
    return {"status": "pass", "message": "ambient exchange deterministic"}

