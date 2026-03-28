"""FAST test: core NetworkGraph normalization and routing are deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.network_graph_deterministic_ordering"
TEST_TAGS = ["fast", "core", "graph", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from core.graph.network_graph_engine import normalize_network_graph, route_query
    from tools.xstack.compatx.canonical_json import canonical_sha256

    graph_input = {
        "schema_version": "1.0.0",
        "graph_id": "graph.core.test",
        "node_type_schema_id": "core.node.payload",
        "edge_type_schema_id": "core.edge.payload",
        "nodes": [
            {"schema_version": "1.0.0", "node_id": "node.c", "node_type_id": "type.generic", "payload_ref": {}, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.a", "node_type_id": "type.generic", "payload_ref": {}, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.b", "node_type_id": "type.generic", "payload_ref": {}, "tags": [], "extensions": {}}
        ],
        "edges": [
            {"schema_version": "1.0.0", "edge_id": "edge.bc", "from_node_id": "node.b", "to_node_id": "node.c", "edge_type_id": "mode", "payload_ref": {}, "capacity": 10, "delay_ticks": 1, "loss_fraction": 0, "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.ab", "from_node_id": "node.a", "to_node_id": "node.b", "edge_type_id": "mode", "payload_ref": {}, "capacity": 10, "delay_ticks": 1, "loss_fraction": 0, "extensions": {}}
        ],
        "deterministic_routing_policy_id": "route.shortest_delay",
        "extensions": {}
    }
    policy = {
        "policy_id": "route.shortest_delay",
        "tie_break_policy": "edge_id_lexicographic",
        "allow_multi_hop": True,
        "optimization_metric": "delay_ticks",
    }

    normalized_a = normalize_network_graph(graph_input)
    normalized_b = normalize_network_graph(graph_input)
    if normalized_a != normalized_b:
        return {"status": "fail", "message": "normalize_network_graph returned non-deterministic payloads"}

    node_ids = [str(row.get("node_id", "")) for row in list(normalized_a.get("nodes") or [])]
    edge_ids = [str(row.get("edge_id", "")) for row in list(normalized_a.get("edges") or [])]
    if node_ids != sorted(node_ids) or edge_ids != sorted(edge_ids):
        return {"status": "fail", "message": "NetworkGraph normalization must sort node/edge IDs deterministically"}

    route_a = route_query(normalized_a, policy, "node.a", "node.c")
    route_b = route_query(normalized_a, policy, "node.a", "node.c")
    if route_a != ["edge.ab", "edge.bc"] or route_b != route_a:
        return {"status": "fail", "message": "route_query did not produce deterministic shortest path output"}

    hash_a = canonical_sha256({"graph": normalized_a, "route": route_a})
    hash_b = canonical_sha256({"graph": normalized_b, "route": route_b})
    if hash_a != hash_b:
        return {"status": "fail", "message": "NetworkGraph canonical hash diverged for identical inputs"}

    return {"status": "pass", "message": "NetworkGraph deterministic ordering passed"}

