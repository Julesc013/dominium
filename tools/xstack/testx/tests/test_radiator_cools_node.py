"""FAST test: THERM-3 radiator exchange cools boundary nodes."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_radiator_cools_node"
TEST_TAGS = ["fast", "thermal", "cooling"]


def _configure_radiator(graph: dict, *, forced_on: bool) -> dict:
    out = copy.deepcopy(graph)
    for node in list(out.get("nodes") or []):
        if str(node.get("node_id", "")).strip() != "node.therm.source":
            continue
        payload = dict(node.get("payload") or {})
        payload["node_kind"] = "radiator"
        ext = dict(payload.get("extensions") or {})
        ext["boundary_to_ambient"] = True
        ext["ambient_coupling_coefficient"] = 240
        ext["base_conductance"] = 320
        ext["forced_cooling_multiplier"] = 1800
        ext["forced_cooling_on"] = bool(forced_on)
        ext["radiator_profile_id"] = "radiator.forced_basic"
        payload["extensions"] = ext
        node["payload"] = payload
    return out


def _source_radiator_row(result: dict) -> dict:
    rows = [
        dict(row)
        for row in list(result.get("radiator_exchange_rows") or [])
        if isinstance(row, dict) and str(row.get("node_id", "")).strip() == "node.therm.source"
    ]
    return dict(rows[0]) if rows else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = build_thermal_graph(source_energy=9000, sink_energy=200, conductance_value=0)
    forced_result = solve_thermal_network_t1(
        graph_row=_configure_radiator(graph, forced_on=True),
        current_tick=300,
        ambient_temperature=10,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    passive_result = solve_thermal_network_t1(
        graph_row=_configure_radiator(graph, forced_on=False),
        current_tick=300,
        ambient_temperature=10,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    forced_row = _source_radiator_row(forced_result)
    passive_row = _source_radiator_row(passive_result)
    if not forced_row:
        return {"status": "fail", "message": "expected radiator exchange row for source node"}
    if not passive_row:
        return {"status": "fail", "message": "expected passive radiator exchange row for source node"}
    if int(forced_row.get("delta_thermal_energy", 0)) >= 0:
        return {"status": "fail", "message": "forced radiator should remove thermal energy"}
    forced_exchange = int(max(0, int(forced_row.get("heat_exchange", 0))))
    passive_exchange = int(max(0, int(passive_row.get("heat_exchange", 0))))
    if forced_exchange <= passive_exchange:
        return {"status": "fail", "message": "forced cooling should exchange more heat than passive mode"}
    return {"status": "pass", "message": "radiator cooling reduces source temperature"}
