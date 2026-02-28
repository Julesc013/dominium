"""FAST test: core routing tie-breaks are deterministic for equal-cost paths."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.routing_deterministic_tie_break"
TEST_TAGS = ["fast", "core", "graph", "routing", "determinism"]


def _graph_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.core.tie_break",
        "node_type_schema_id": "core.node.payload",
        "edge_type_schema_id": "core.edge.payload",
        "payload_schema_versions": {
            "core.node.payload": "1.0.0",
            "core.edge.payload": "1.0.0",
        },
        "validation_mode": "strict",
        "nodes": [
            {"schema_version": "1.0.0", "node_id": "node.a", "node_type_id": "kind.node", "payload_ref": {}, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.b", "node_type_id": "kind.node", "payload_ref": {}, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.c", "node_type_id": "kind.node", "payload_ref": {}, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.d", "node_type_id": "kind.node", "payload_ref": {}, "tags": [], "extensions": {}},
        ],
        "edges": [
            {"schema_version": "1.0.0", "edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 10, "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.b_d", "from_node_id": "node.b", "to_node_id": "node.d", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 10, "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.a_c", "from_node_id": "node.a", "to_node_id": "node.c", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 10, "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.c_d", "from_node_id": "node.c", "to_node_id": "node.d", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 10, "extensions": {}},
        ],
        "deterministic_routing_policy_id": "route.shortest_delay",
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.graph.routing_engine import query_route_result

    graph = _graph_payload()
    policy = {
        "policy_id": "route.shortest_delay",
        "description": "deterministic shortest delay",
        "tie_break_policy": "edge_id_lexicographic",
        "allow_multi_hop": True,
        "optimization_metric": "delay_ticks",
        "extensions": {},
    }
    first = query_route_result(
        graph_row=graph,
        routing_policy_row=policy,
        from_node_id="node.a",
        to_node_id="node.d",
        constraints_row={},
        cache_state={"entries_by_key": {}, "next_sequence": 0},
        max_cache_entries=16,
    )
    second = query_route_result(
        graph_row=graph,
        routing_policy_row=policy,
        from_node_id="node.a",
        to_node_id="node.d",
        constraints_row={},
        cache_state={"entries_by_key": {}, "next_sequence": 0},
        max_cache_entries=16,
    )
    route_a = list((dict(first.get("route_result") or {})).get("path_edge_ids") or [])
    route_b = list((dict(second.get("route_result") or {})).get("path_edge_ids") or [])
    expected = ["edge.a_b", "edge.b_d"]
    if route_a != expected or route_b != expected:
        return {
            "status": "fail",
            "message": "routing tie-break must pick lexicographically smallest equal-cost edge sequence",
        }
    if dict(first.get("route_result") or {}) != dict(second.get("route_result") or {}):
        return {"status": "fail", "message": "route_result diverged across identical inputs"}
    return {"status": "pass", "message": "routing deterministic tie-break passed"}

