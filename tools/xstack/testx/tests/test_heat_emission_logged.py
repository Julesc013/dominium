"""FAST test: THERM-4 combustion heat emission is logged in events/hazards."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_heat_emission_logged"
TEST_TAGS = ["fast", "thermal", "fire", "logging"]


def _burning_graph() -> dict:
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = build_thermal_graph(source_energy=35000, sink_energy=100, conductance_value=0)
    for node in list(graph.get("nodes") or []):
        if str(node.get("node_id", "")).strip() != "node.therm.source":
            continue
        payload = dict(node.get("payload") or {})
        ext = dict(payload.get("extensions") or {})
        ext["combustible"] = True
        ext["material_id"] = "material.wood_basic"
        ext["oxygen_available"] = True
        payload["extensions"] = ext
        node["payload"] = payload
    return graph


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from thermal.network.thermal_network_engine import solve_thermal_network_t1

    result = solve_thermal_network_t1(
        graph_row=copy.deepcopy(_burning_graph()),
        current_tick=104,
        max_cost_units=4096,
        fire_state_rows=[
            {
                "schema_version": "1.0.0",
                "target_id": "node.therm.source",
                "active": True,
                "fuel_remaining": 900,
                "last_update_tick": 103,
                "deterministic_fingerprint": "",
                "extensions": {"material_id": "material.wood_basic"},
            }
        ],
    )
    events = [dict(row) for row in list(result.get("fire_event_rows") or []) if isinstance(row, dict)]
    if not events:
        return {"status": "fail", "message": "expected fire events for active combustion"}
    if not any(int(row.get("heat_emission", 0)) > 0 for row in events):
        return {"status": "fail", "message": "expected non-zero heat_emission in fire event rows"}
    hazards = [
        dict(row)
        for row in list(result.get("hazard_rows") or [])
        if isinstance(row, dict) and str(row.get("hazard_type_id", "")).strip() == "hazard.fire.basic"
    ]
    if not hazards:
        return {"status": "fail", "message": "expected hazard.fire.basic increment from combustion output"}
    return {"status": "pass", "message": "combustion heat emission and hazard increment logged"}

