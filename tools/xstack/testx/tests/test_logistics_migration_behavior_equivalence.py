"""FAST test: logistics behavior remains equivalent after core graph/flow substrate migration."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.logistics_migration_behavior_equivalence"
TEST_TAGS = ["fast", "materials", "logistics", "migration", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logistics.logistics_engine import (
        REFUSAL_LOGISTICS_INVALID_ROUTE,
        LogisticsError,
        build_inventory_index,
        create_manifest_and_commitment,
        tick_manifests,
    )
    from tools.xstack.testx.tests.logistics_testlib import (
        FIXED_POINT_SCALE,
        logistics_routing_rule_registry,
        with_inventory,
        base_state,
    )

    graph = {
        "schema_version": "1.0.0",
        "graph_id": "graph.logistics.migration.eq",
        "nodes": [
            {"schema_version": "1.0.0", "node_id": "node.alpha", "node_type": "depot", "location_ref": "site.alpha", "capacity_storage": 10000, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.beta", "node_type": "depot", "location_ref": "site.beta", "capacity_storage": 10000, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.gamma", "node_type": "depot", "location_ref": "site.gamma", "capacity_storage": 10000, "tags": [], "extensions": {}},
        ],
        "edges": [
            {"schema_version": "1.0.0", "edge_id": "edge.direct", "from_node_id": "node.alpha", "to_node_id": "node.beta", "transport_mode": "road", "capacity_mass_per_tick": 1000, "delay_ticks": 1, "loss_fraction": 0, "cost_units_per_mass": 50, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.a_g", "from_node_id": "node.alpha", "to_node_id": "node.gamma", "transport_mode": "road", "capacity_mass_per_tick": 1000, "delay_ticks": 1, "loss_fraction": 0, "cost_units_per_mass": 1, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "edge_id": "edge.g_b", "from_node_id": "node.gamma", "to_node_id": "node.beta", "transport_mode": "road", "capacity_mass_per_tick": 1000, "delay_ticks": 1, "loss_fraction": 0, "cost_units_per_mass": 1, "tags": [], "extensions": {}},
        ],
        "deterministic_routing_rule_id": "route.min_cost_units",
        "version_introduced": "1.0.0",
        "extensions": {},
    }

    routing_rule_rows = (logistics_routing_rule_registry().get("routing_rules") or [])
    routing_rule = next((dict(row) for row in routing_rule_rows if str(row.get("rule_id", "")) == "route.min_cost_units"), None)
    if not routing_rule:
        return {"status": "fail", "message": "test fixture missing route.min_cost_units routing rule"}

    state = with_inventory(base_state(), node_id="node.alpha", material_id="material.steel_basic", mass=2000, batch_id="batch.seed")
    inventory_index = build_inventory_index(list(state.get("logistics_node_inventories") or []))

    created = create_manifest_and_commitment(
        graph_row=graph,
        routing_rule_row=routing_rule,
        inventory_index=inventory_index,
        from_node_id="node.alpha",
        to_node_id="node.beta",
        batch_id="batch.seed",
        material_id="material.steel_basic",
        quantity_mass=500,
        earliest_depart_tick=0,
        actor_subject_id="subject.test",
        intent_id="intent.test.migration.eq",
        current_tick=0,
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64}},
    )
    route_edge_ids = list(created.get("route_edge_ids") or [])
    if route_edge_ids != ["edge.a_g", "edge.g_b"]:
        return {"status": "fail", "message": "route.min_cost_units deterministic route selection changed after migration"}

    first_tick = tick_manifests(
        graph_row=graph,
        manifests=[dict(created.get("manifest") or {})],
        commitments=[dict(created.get("commitment") or {})],
        inventory_index=copy.deepcopy(created.get("inventory_index") or {}),
        current_tick=0,
        max_updates=8,
        actor_subject_id="subject.test",
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64}},
    )
    second_tick = tick_manifests(
        graph_row=graph,
        manifests=list(first_tick.get("manifests") or []),
        commitments=list(first_tick.get("commitments") or []),
        inventory_index=copy.deepcopy(first_tick.get("inventory_index") or {}),
        current_tick=2,
        max_updates=8,
        actor_subject_id="subject.test",
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64}},
        event_sequence_start=int(first_tick.get("next_event_sequence", 0) or 0),
    )

    rows = list(second_tick.get("manifests") or [])
    if len(rows) != 1 or str((dict(rows[0]).get("status", ""))) != "delivered":
        return {"status": "fail", "message": "manifest delivery semantics changed after migration"}

    inventories = dict(second_tick.get("inventory_index") or {})
    source_mass = int((dict((dict(inventories.get("node.alpha") or {})).get("material_stocks") or {})).get("material.steel_basic", 0))
    destination_mass = int((dict((dict(inventories.get("node.beta") or {})).get("material_stocks") or {})).get("material.steel_basic", 0))
    if source_mass != 1500 or destination_mass != 500:
        return {"status": "fail", "message": "inventory debit/credit behavior changed after migration"}

    try:
        create_manifest_and_commitment(
            graph_row=graph,
            routing_rule_row={"rule_id": "route.direct_only", "description": "", "tie_break_policy": "edge_id_lexicographic", "allow_multi_hop": False, "constraints": {}, "extensions": {}},
            inventory_index=build_inventory_index(list(state.get("logistics_node_inventories") or [])),
            from_node_id="node.alpha",
            to_node_id="node.missing",
            batch_id="batch.seed",
            material_id="material.steel_basic",
            quantity_mass=100,
            earliest_depart_tick=0,
            actor_subject_id="subject.test",
            intent_id="intent.test.migration.eq.refusal",
            current_tick=0,
            numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64, "scale": FIXED_POINT_SCALE}},
        )
    except LogisticsError as exc:
        if str(exc.reason_code) != REFUSAL_LOGISTICS_INVALID_ROUTE:
            return {"status": "fail", "message": "invalid-route refusal code changed after migration"}
    else:
        return {"status": "fail", "message": "invalid route should refuse deterministically after migration"}

    return {"status": "pass", "message": "Logistics migration behavior equivalence passed"}

