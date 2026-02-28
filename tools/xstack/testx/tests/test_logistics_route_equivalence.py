"""FAST test: logistics routing remains equivalent to core routing substrate queries."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.logistics_route_equivalence"
TEST_TAGS = ["fast", "materials", "logistics", "routing", "determinism", "migration"]


def _graph_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.logistics.route_equiv",
        "nodes": [
            {"schema_version": "1.0.0", "node_id": "node.alpha", "node_type": "depot", "location_ref": "site.alpha", "capacity_storage": 10000, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.beta", "node_type": "depot", "location_ref": "site.beta", "capacity_storage": 10000, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.gamma", "node_type": "depot", "location_ref": "site.gamma", "capacity_storage": 10000, "tags": [], "extensions": {}},
        ],
        "edges": [
            {"schema_version": "1.0.0", "edge_id": "edge.direct", "from_node_id": "node.alpha", "to_node_id": "node.beta", "transport_mode": "road", "capacity_mass_per_tick": 1000, "delay_ticks": 1, "loss_fraction": 0, "cost_units_per_mass": 50, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.a_g", "from_node_id": "node.alpha", "to_node_id": "node.gamma", "transport_mode": "road", "capacity_mass_per_tick": 1000, "delay_ticks": 2, "loss_fraction": 0, "cost_units_per_mass": 1, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.g_b", "from_node_id": "node.gamma", "to_node_id": "node.beta", "transport_mode": "road", "capacity_mass_per_tick": 1000, "delay_ticks": 2, "loss_fraction": 0, "cost_units_per_mass": 1, "tags": [], "extensions": {}},
        ],
        "deterministic_routing_rule_id": "route.shortest_delay",
        "version_introduced": "1.0.0",
        "extensions": {},
    }


def _rule(rule_id: str, allow_multi_hop: bool) -> dict:
    return {
        "schema_version": "1.0.0",
        "rule_id": rule_id,
        "description": "test rule",
        "tie_break_policy": "edge_id_lexicographic",
        "allow_multi_hop": bool(allow_multi_hop),
        "constraints": {},
        "extensions": {},
    }


def _create_manifest_route(*, graph: dict, rule: dict, inventory_index: dict):
    from src.logistics.logistics_engine import create_manifest_and_commitment

    created = create_manifest_and_commitment(
        graph_row=graph,
        routing_rule_row=rule,
        inventory_index=inventory_index,
        from_node_id="node.alpha",
        to_node_id="node.beta",
        batch_id="batch.route_equiv",
        material_id="material.steel_basic",
        quantity_mass=100,
        earliest_depart_tick=0,
        actor_subject_id="subject.test",
        intent_id="intent.logistics.route_equiv",
        current_tick=0,
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64}},
    )
    return list(created.get("route_edge_ids") or [])


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.graph.routing_engine import route_query_edges
    from src.logistics.logistics_engine import _core_graph_payload, _core_routing_policy, build_inventory_index

    graph = _graph_payload()
    inventory_index = build_inventory_index(
        [
            {
                "schema_version": "1.0.0",
                "node_id": "node.alpha",
                "material_stocks": {"material.steel_basic": 1000},
                "batch_refs": ["batch.route_equiv"],
                "inventory_hash": "",
                "extensions": {},
            }
        ]
    )

    shortest_rule = _rule("route.shortest_delay", allow_multi_hop=True)
    core_shortest = route_query_edges(
        _core_graph_payload(graph),
        _core_routing_policy(shortest_rule),
        "node.alpha",
        "node.beta",
        constraints_row={},
    )
    logistics_shortest = _create_manifest_route(
        graph=graph,
        rule=shortest_rule,
        inventory_index=copy.deepcopy(inventory_index),
    )
    if logistics_shortest != core_shortest:
        return {"status": "fail", "message": "shortest-delay logistics route diverged from core routing substrate"}

    min_cost_rule = _rule("route.min_cost_units", allow_multi_hop=True)
    core_min_cost = route_query_edges(
        _core_graph_payload(graph),
        _core_routing_policy(min_cost_rule),
        "node.alpha",
        "node.beta",
        constraints_row={},
    )
    logistics_min_cost = _create_manifest_route(
        graph=graph,
        rule=min_cost_rule,
        inventory_index=copy.deepcopy(inventory_index),
    )
    if logistics_min_cost != core_min_cost:
        return {"status": "fail", "message": "min-cost logistics route diverged from core routing substrate"}

    if core_shortest != ["edge.direct"]:
        return {"status": "fail", "message": "shortest-delay route expectation mismatch"}
    if core_min_cost != ["edge.a_g", "edge.g_b"]:
        return {"status": "fail", "message": "min-cost route expectation mismatch"}
    return {"status": "pass", "message": "logistics route equivalence to core routing passed"}

