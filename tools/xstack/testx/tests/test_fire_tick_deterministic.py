"""FAST test: THERM-4 fire tick evolution is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_fire_tick_deterministic"
TEST_TAGS = ["fast", "thermal", "fire", "determinism"]


def _seed_burning_graph() -> dict:
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = build_thermal_graph(source_energy=40000, sink_energy=100, conductance_value=0)
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

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1

    graph = _seed_burning_graph()
    fire_rows = [
        {
            "schema_version": "1.0.0",
            "target_id": "node.therm.source",
            "active": True,
            "fuel_remaining": 1200,
            "last_update_tick": 5,
            "deterministic_fingerprint": "",
            "extensions": {"material_id": "material.wood_basic"},
        }
    ]
    first = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=88,
        max_cost_units=4096,
        fire_state_rows=copy.deepcopy(fire_rows),
    )
    second = solve_thermal_network_t1(
        graph_row=copy.deepcopy(graph),
        current_tick=88,
        max_cost_units=4096,
        fire_state_rows=copy.deepcopy(fire_rows),
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "fire tick solve diverged for identical inputs"}
    first_rows = [dict(row) for row in list(first.get("fire_state_rows") or []) if isinstance(row, dict)]
    if not first_rows:
        return {"status": "fail", "message": "expected fire_state_rows in THERM-4 output"}
    fuel_after = int(first_rows[0].get("fuel_remaining", 0))
    if fuel_after >= 1200:
        return {"status": "fail", "message": "fire tick should consume fuel deterministically"}
    if str(first.get("fire_state_hash_chain", "")).strip() != str(second.get("fire_state_hash_chain", "")).strip():
        return {"status": "fail", "message": "fire_state_hash_chain drifted across identical runs"}
    return {"status": "pass", "message": "fire tick deterministic"}

