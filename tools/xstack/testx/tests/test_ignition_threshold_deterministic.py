"""FAST test: THERM-4 ignition threshold behavior is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_ignition_threshold_deterministic"
TEST_TAGS = ["fast", "thermal", "fire", "determinism"]


def _set_combustible(graph: dict, *, source_energy: int) -> dict:
    out = copy.deepcopy(graph)
    for node in list(out.get("nodes") or []):
        if str(node.get("node_id", "")).strip() != "node.therm.source":
            continue
        payload = dict(node.get("payload") or {})
        payload["current_thermal_energy"] = int(max(0, int(source_energy)))
        ext = dict(payload.get("extensions") or {})
        ext["combustible"] = True
        ext["material_id"] = "material.wood_basic"
        ext["oxygen_available"] = True
        payload["extensions"] = ext
        node["payload"] = payload
    return out


def _started_count(result: dict) -> int:
    return len(
        [
            row
            for row in list(result.get("fire_event_rows") or [])
            if isinstance(row, dict) and str(row.get("event_type", "")).strip() in {"event.fire_started", "event.fire_spread_started"}
        ]
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    hot_graph = _set_combustible(build_thermal_graph(source_energy=60000, sink_energy=100, conductance_value=0), source_energy=60000)
    cool_graph = _set_combustible(build_thermal_graph(source_energy=500, sink_energy=100, conductance_value=0), source_energy=500)

    hot_a = solve_thermal_network_t1(graph_row=copy.deepcopy(hot_graph), current_tick=77, max_cost_units=4096)
    hot_b = solve_thermal_network_t1(graph_row=copy.deepcopy(hot_graph), current_tick=77, max_cost_units=4096)
    cool = solve_thermal_network_t1(graph_row=copy.deepcopy(cool_graph), current_tick=77, max_cost_units=4096)

    if dict(hot_a) != dict(hot_b):
        return {"status": "fail", "message": "hot ignition solve diverged across identical runs"}
    if _started_count(hot_a) <= 0:
        return {"status": "fail", "message": "expected ignition for hot combustible node above threshold"}
    if _started_count(cool) != 0:
        return {"status": "fail", "message": "cool node should not ignite below ignition threshold"}
    return {"status": "pass", "message": "ignition threshold behavior deterministic"}

