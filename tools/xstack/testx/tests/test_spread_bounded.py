"""FAST test: THERM-4 spread is deterministically bounded by configured cap."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_spread_bounded"
TEST_TAGS = ["fast", "thermal", "fire", "budget", "determinism"]


def _node(node_id: str) -> dict:
    return {
        "node_id": node_id,
        "node_type_id": "node.therm.mass",
        "tags": ["thermal"],
        "payload": {
            "schema_version": "1.0.0",
            "node_kind": "thermal_mass",
            "heat_capacity_value": 100,
            "current_thermal_energy": 60000,
            "spec_id": None,
            "model_bindings": [],
            "safety_instances": [],
            "deterministic_fingerprint": "",
            "extensions": {
                "combustible": True,
                "material_id": "material.wood_basic",
                "oxygen_available": True,
            },
        },
    }


def _edge(edge_id: str, src: str, dst: str) -> dict:
    return {
        "edge_id": edge_id,
        "from_node_id": src,
        "to_node_id": dst,
        "edge_type_id": "edge.therm.conduction",
        "capacity": 0,
        "delay_ticks": 0,
        "cost_units": 1,
        "payload": {
            "schema_version": "1.0.0",
            "edge_kind": "conduction_link",
            "conductance_value": 0,
            "spec_id": None,
            "model_bindings": [],
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        "extensions": {},
    }


def _spread_graph() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.therm.spread",
        "node_type_schema_id": "dominium.schema.thermal.thermal_node_payload.v1",
        "edge_type_schema_id": "dominium.schema.thermal.thermal_edge_payload.v1",
        "payload_schema_versions": {
            "dominium.schema.thermal.thermal_node_payload.v1": "1.0.0",
            "dominium.schema.thermal.thermal_edge_payload.v1": "1.0.0",
        },
        "validation_mode": "strict",
        "deterministic_routing_policy_id": "route.shortest_delay",
        "graph_partition_id": None,
        "nodes": [
            _node("node.therm.source"),
            _node("node.therm.n1"),
            _node("node.therm.n2"),
            _node("node.therm.n3"),
        ],
        "edges": [
            _edge("edge.therm.1", "node.therm.source", "node.therm.n1"),
            _edge("edge.therm.2", "node.therm.source", "node.therm.n2"),
            _edge("edge.therm.3", "node.therm.source", "node.therm.n3"),
        ],
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1

    first = solve_thermal_network_t1(
        graph_row=_spread_graph(),
        current_tick=91,
        max_cost_units=4096,
        fire_state_rows=[
            {
                "schema_version": "1.0.0",
                "target_id": "node.therm.source",
                "active": True,
                "fuel_remaining": 1200,
                "last_update_tick": 90,
                "deterministic_fingerprint": "",
                "extensions": {"material_id": "material.wood_basic"},
            }
        ],
        max_fire_spread_per_tick=1,
        fire_iteration_limit=4,
    )
    second = solve_thermal_network_t1(
        graph_row=_spread_graph(),
        current_tick=91,
        max_cost_units=4096,
        fire_state_rows=[
            {
                "schema_version": "1.0.0",
                "target_id": "node.therm.source",
                "active": True,
                "fuel_remaining": 1200,
                "last_update_tick": 90,
                "deterministic_fingerprint": "",
                "extensions": {"material_id": "material.wood_basic"},
            }
        ],
        max_fire_spread_per_tick=1,
        fire_iteration_limit=4,
    )
    spread_events = [
        dict(row)
        for row in list(first.get("fire_event_rows") or [])
        if isinstance(row, dict) and str(row.get("event_type", "")).strip() == "event.fire_spread_started"
    ]
    if len(spread_events) > 1:
        return {"status": "fail", "message": "spread exceeded deterministic cap of 1 ignition per tick"}
    degrade_rows = [
        dict(row)
        for row in list(first.get("decision_log_rows") or [])
        if isinstance(row, dict) and str(row.get("reason_code", "")).strip() == "degrade.therm.fire_spread_cap"
    ]
    if not degrade_rows:
        return {"status": "fail", "message": "expected spread cap degradation log when adjacency exceeds cap"}
    if str(first.get("fire_spread_hash_chain", "")).strip() != str(second.get("fire_spread_hash_chain", "")).strip():
        return {"status": "fail", "message": "fire_spread_hash_chain drifted across identical runs"}
    return {"status": "pass", "message": "fire spread is bounded and deterministic"}

