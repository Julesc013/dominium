"""FAST test: cross-shard flow transfer plans are deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.core.cross_shard_flow_plan_deterministic"
TEST_TAGS = ["fast", "core", "flow", "partition", "determinism"]


def _graph_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.core.flow.partition",
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
            {"schema_version": "1.0.0", "edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 1000, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.b_c", "from_node_id": "node.b", "to_node_id": "node.c", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 1000, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "extensions": {}},
        ],
        "deterministic_routing_policy_id": "route.shortest_delay",
        "extensions": {},
    }


def _partition_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "partition_id": "partition.graph.core.flow.partition",
        "graph_id": "graph.core.flow.partition",
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


def _channel() -> dict:
    return {
        "schema_version": "1.0.0",
        "channel_id": "flow.channel.partition.alpha",
        "graph_id": "graph.core.flow.partition",
        "quantity_id": "quantity.mass",
        "source_node_id": "node.a",
        "sink_node_id": "node.c",
        "capacity_per_tick": 100,
        "delay_ticks": 0,
        "loss_fraction": 0,
        "solver_policy_id": "flow.coarse_default",
        "priority": 0,
        "extensions": {
            "route_edge_ids": ["edge.a_b", "edge.b_c"],
            "route_node_ids": ["node.a", "node.b", "node.c"],
        },
    }


def _solver() -> dict:
    return {
        "flow.coarse_default": {
            "schema_version": "1.0.0",
            "solver_policy_id": "flow.coarse_default",
            "mode": "bulk",
            "allow_partial_transfer": True,
            "overflow_policy": "queue",
            "extensions": {},
        }
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.flow.flow_engine import tick_flow_channels

    args = {
        "channels": [_channel()],
        "node_balances": {"node.a": 100, "node.c": 0},
        "current_tick": 0,
        "fixed_point_scale": 1000,
        "solver_policies": _solver(),
        "conserved_quantity_ids": ["quantity.mass"],
        "max_channels": 4,
        "strict_budget": False,
        "sink_capacities": {},
        "channel_runtime": {},
        "graph_row": _graph_payload(),
        "partition_row": _partition_payload(),
        "cost_units_per_channel": 1,
    }
    first = tick_flow_channels(**copy.deepcopy(args))
    second = tick_flow_channels(**copy.deepcopy(args))
    if first != second:
        return {"status": "fail", "message": "cross-shard flow planning diverged across equivalent runs"}
    plans = list(first.get("cross_shard_transfer_plans") or [])
    if len(plans) != 1:
        return {"status": "fail", "message": "expected one cross-shard flow plan"}
    plan = dict((dict(plans[0]).get("plan") or {}))
    if not bool(plan.get("partitioned", False)):
        return {"status": "fail", "message": "cross-shard flow plan must be marked partitioned"}
    if len(list(plan.get("segments") or [])) != 2:
        return {"status": "fail", "message": "cross-shard flow plan must include two deterministic segments"}
    boundaries = list(plan.get("cross_shard_boundaries") or [])
    if len(boundaries) != 1 or str((dict(boundaries[0]).get("boundary_node_id", ""))) != "node.b":
        return {"status": "fail", "message": "cross-shard flow boundary node mismatch"}
    return {"status": "pass", "message": "cross-shard flow plan deterministic behavior passed"}

