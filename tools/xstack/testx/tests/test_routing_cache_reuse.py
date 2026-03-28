"""FAST test: core routing cache key reuse is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.routing_cache_reuse"
TEST_TAGS = ["fast", "core", "graph", "routing", "cache", "determinism"]


def _graph_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.core.cache",
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
        ],
        "edges": [
            {"schema_version": "1.0.0", "edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 2, "loss_fraction": 0, "cost_units": 20, "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.b_c", "from_node_id": "node.b", "to_node_id": "node.c", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 3, "loss_fraction": 0, "cost_units": 30, "extensions": {}},
        ],
        "deterministic_routing_policy_id": "route.shortest_delay",
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from core.graph.routing_engine import query_route_result

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
        to_node_id="node.c",
        cache_state={"entries_by_key": {}, "next_sequence": 0},
        max_cache_entries=8,
    )
    second = query_route_result(
        graph_row=graph,
        routing_policy_row=policy,
        from_node_id="node.a",
        to_node_id="node.c",
        cache_state=dict(first.get("cache_state") or {}),
        max_cache_entries=8,
    )
    if bool(first.get("cache_hit", False)):
        return {"status": "fail", "message": "first route query should not be a cache hit"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "second route query should reuse cache deterministically"}
    if str(first.get("cache_key", "")) != str(second.get("cache_key", "")):
        return {"status": "fail", "message": "route cache keys diverged across equivalent queries"}
    if dict(first.get("route_result") or {}) != dict(second.get("route_result") or {}):
        return {"status": "fail", "message": "cached route_result changed between repeated queries"}
    return {"status": "pass", "message": "routing cache reuse deterministic"}

