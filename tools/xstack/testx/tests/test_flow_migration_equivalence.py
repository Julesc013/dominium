"""FAST test: logistics transfer semantics remain equivalent after FlowSystem migration."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.flow_migration_equivalence"
TEST_TAGS = ["fast", "materials", "logistics", "flow", "migration", "determinism"]


def _graph() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.logistics.flow.eq",
        "nodes": [
            {"schema_version": "1.0.0", "node_id": "node.alpha", "node_type": "depot", "location_ref": "site.alpha", "capacity_storage": 10000, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.beta", "node_type": "depot", "location_ref": "site.beta", "capacity_storage": 10000, "tags": [], "extensions": {}},
        ],
        "edges": [
            {"schema_version": "1.0.0", "edge_id": "edge.alpha_beta", "from_node_id": "node.alpha", "to_node_id": "node.beta", "transport_mode": "road", "capacity_mass_per_tick": 1000, "delay_ticks": 0, "loss_fraction": 0, "cost_units_per_mass": 1, "tags": [], "extensions": {}},
        ],
        "deterministic_routing_rule_id": "route.direct_only",
        "version_introduced": "1.0.0",
        "extensions": {},
    }


def _routing_rule() -> dict:
    return {
        "schema_version": "1.0.0",
        "rule_id": "route.direct_only",
        "description": "direct only",
        "tie_break_policy": "edge_id_lexicographic",
        "allow_multi_hop": False,
        "constraints": {},
        "extensions": {},
    }


def _solver_registry() -> dict:
    return {
        "solver_policies": [
            {
                "schema_version": "1.0.0",
                "solver_policy_id": "flow.coarse_default",
                "mode": "bulk",
                "allow_partial_transfer": True,
                "overflow_policy": "queue",
                "extensions": {},
            }
        ]
    }


def _run_once():
    from logistics.logistics_engine import (
        build_inventory_index,
        create_manifest_and_commitment,
        tick_manifests,
    )

    inventory = build_inventory_index(
        [
            {
                "schema_version": "1.0.0",
                "node_id": "node.alpha",
                "material_stocks": {"material.steel_basic": 2000},
                "batch_refs": ["batch.seed"],
                "inventory_hash": "",
                "extensions": {},
            }
        ]
    )
    created = create_manifest_and_commitment(
        graph_row=_graph(),
        routing_rule_row=_routing_rule(),
        inventory_index=copy.deepcopy(inventory),
        from_node_id="node.alpha",
        to_node_id="node.beta",
        batch_id="batch.seed",
        material_id="material.steel_basic",
        quantity_mass=750,
        earliest_depart_tick=0,
        actor_subject_id="subject.test",
        intent_id="intent.flow.eq",
        current_tick=0,
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64}},
        flow_solver_policy_registry=_solver_registry(),
    )
    ticked = tick_manifests(
        graph_row=_graph(),
        manifests=[dict(created.get("manifest") or {})],
        commitments=[dict(created.get("commitment") or {})],
        inventory_index=copy.deepcopy(created.get("inventory_index") or {}),
        current_tick=0,
        max_updates=8,
        actor_subject_id="subject.test",
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64}},
        event_sequence_start=0,
        flow_solver_policy_registry=_solver_registry(),
        graph_partition_row={},
    )
    return created, ticked


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    created_a, ticked_a = _run_once()
    created_b, ticked_b = _run_once()
    if created_a != created_b or ticked_a != ticked_b:
        return {"status": "fail", "message": "flow migration logistics outputs diverged across equivalent runs"}
    manifest = dict((list(ticked_a.get("manifests") or [{}]) or [{}])[0])
    if str(manifest.get("status", "")) != "delivered":
        return {"status": "fail", "message": "flow migration changed manifest delivery semantics"}
    inv = dict(ticked_a.get("inventory_index") or {})
    source_mass = int((dict((dict(inv.get("node.alpha") or {})).get("material_stocks") or {})).get("material.steel_basic", 0))
    sink_mass = int((dict((dict(inv.get("node.beta") or {})).get("material_stocks") or {})).get("material.steel_basic", 0))
    if source_mass != 1250 or sink_mass != 750:
        return {"status": "fail", "message": "flow migration changed source/sink inventory mass accounting"}
    flow_events = list(ticked_a.get("flow_transfer_events") or [])
    if len(flow_events) != 1:
        return {"status": "fail", "message": "expected one deterministic flow transfer event for manifest delivery"}
    event = dict(flow_events[0])
    if int(event.get("transferred_amount", -1)) != 750 or int(event.get("lost_amount", -1)) != 0:
        return {"status": "fail", "message": "flow transfer event payload mismatch for migration equivalence"}
    return {"status": "pass", "message": "flow migration logistics equivalence passed"}

