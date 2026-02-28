"""FAST test: partition-aware route plans are deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.partition_route_plan_deterministic"
TEST_TAGS = ["fast", "core", "graph", "routing", "partition", "determinism"]


def _graph_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.core.partition",
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
            {"schema_version": "1.0.0", "edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.b_c", "from_node_id": "node.b", "to_node_id": "node.c", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "extensions": {}},
        ],
        "deterministic_routing_policy_id": "route.shortest_delay",
        "extensions": {},
    }


def _partition_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "partition_id": "partition.graph.core.partition",
        "graph_id": "graph.core.partition",
        "node_shard_map": {
            "node.a": "shard.alpha",
            "node.b": "shard.alpha",
            "node.c": "shard.beta",
        },
        "edge_shard_map": {
            "edge.a_b": "shard.alpha",
            "edge.b_c": "shard.beta",
        },
        "cross_shard_boundary_nodes": ["node.b"],
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.graph.routing_engine import query_route_result

    graph = _graph_payload()
    partition = _partition_payload()
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
        partition_row=partition,
        cache_state={"entries_by_key": {}, "next_sequence": 0},
        max_cache_entries=0,
    )
    second = query_route_result(
        graph_row=graph,
        routing_policy_row=policy,
        from_node_id="node.a",
        to_node_id="node.c",
        partition_row=partition,
        cache_state={"entries_by_key": {}, "next_sequence": 0},
        max_cache_entries=0,
    )
    plan_a = dict(first.get("cross_shard_route_plan") or {})
    plan_b = dict(second.get("cross_shard_route_plan") or {})
    if not bool(plan_a.get("partitioned", False)):
        return {"status": "fail", "message": "partition route plan must be marked partitioned when partition metadata exists"}
    segments = list(plan_a.get("segments") or [])
    if len(segments) != 2:
        return {"status": "fail", "message": "partition route plan should split route into two deterministic shard-local segments"}
    boundaries = list(plan_a.get("cross_shard_boundaries") or [])
    if len(boundaries) != 1 or str((dict(boundaries[0]).get("boundary_node_id", ""))) != "node.b":
        return {"status": "fail", "message": "partition boundary segmentation is incorrect"}
    if plan_a != plan_b:
        return {"status": "fail", "message": "partition route plan changed across equivalent route queries"}
    return {"status": "pass", "message": "partition route plan deterministic"}

