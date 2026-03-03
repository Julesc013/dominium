"""FAST test: THERM-3 emits overheat hazards when cooling is insufficient."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_overheat_when_no_cooling"
TEST_TAGS = ["fast", "thermal", "safety"]


def _configure_hot_node(graph: dict) -> dict:
    out = copy.deepcopy(graph)
    for node in list(out.get("nodes") or []):
        if str(node.get("node_id", "")).strip() != "node.therm.source":
            continue
        payload = dict(node.get("payload") or {})
        payload["current_thermal_energy"] = 30000
        ext = dict(payload.get("extensions") or {})
        ext["overtemp_threshold"] = 15
        ext["ambient_coupling_coefficient"] = 0
        ext["boundary_to_ambient"] = False
        payload["extensions"] = ext
        node["payload"] = payload
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = _configure_hot_node(
        build_thermal_graph(source_energy=12000, sink_energy=200, conductance_value=0)
    )
    result = solve_thermal_network_t1(
        graph_row=graph,
        current_tick=420,
        ambient_temperature=10,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    hazard_rows = [
        dict(row)
        for row in list(result.get("hazard_rows") or [])
        if isinstance(row, dict) and str(row.get("hazard_type_id", "")).strip() == "hazard.overheat"
    ]
    safety_rows = [
        dict(row)
        for row in list(result.get("safety_event_rows") or [])
        if isinstance(row, dict) and str(row.get("pattern_id", "")).strip() == "safety.overtemp_trip"
    ]
    if not hazard_rows:
        return {"status": "fail", "message": "expected overheat hazard rows when no cooling exists"}
    if not safety_rows:
        return {"status": "fail", "message": "expected overtemp safety event rows when threshold is exceeded"}
    return {"status": "pass", "message": "overheat hazard and safety trigger emitted"}

