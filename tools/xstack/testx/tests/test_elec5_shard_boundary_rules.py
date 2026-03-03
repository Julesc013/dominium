"""FAST test: ELEC-5 enforces shard boundary node requirements for cross-shard edges."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_shard_boundary_rules"
TEST_TAGS = ["fast", "electric", "elec5", "shard", "boundary"]


def _invalid_cross_shard_graph() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.elec.shard.invalid",
        "node_type_schema_id": "dominium.schema.electric.elec_node_payload.v1",
        "edge_type_schema_id": "dominium.schema.electric.elec_edge_payload.v1",
        "payload_schema_versions": {
            "dominium.schema.electric.elec_node_payload.v1": "1.0.0",
            "dominium.schema.electric.elec_edge_payload.v1": "1.0.0",
        },
        "validation_mode": "strict",
        "deterministic_routing_policy_id": "route.shortest_delay",
        "graph_partition_id": None,
        "nodes": [
            {
                "node_id": "node.elec.boundary.a",
                "node_type_id": "node.elec.bus",
                "tags": ["electric", "bus"],
                "payload": {
                    "schema_version": "1.0.0",
                    "node_kind": "bus",
                    "spec_id": None,
                    "model_bindings": [],
                    "safety_instances": [],
                    "deterministic_fingerprint": "",
                    "extensions": {"shard_id": "shard.01", "boundary_node": False},
                },
                "extensions": {"shard_id": "shard.01", "boundary_node": False},
            },
            {
                "node_id": "node.elec.boundary.b",
                "node_type_id": "node.elec.bus",
                "tags": ["electric", "bus"],
                "payload": {
                    "schema_version": "1.0.0",
                    "node_kind": "bus",
                    "spec_id": None,
                    "model_bindings": [],
                    "safety_instances": [],
                    "deterministic_fingerprint": "",
                    "extensions": {"shard_id": "shard.02", "boundary_node": False},
                },
                "extensions": {"shard_id": "shard.02", "boundary_node": False},
            },
        ],
        "edges": [
            {
                "edge_id": "edge.elec.boundary.invalid",
                "from_node_id": "node.elec.boundary.a",
                "to_node_id": "node.elec.boundary.b",
                "edge_type_id": "edge.elec.conductor",
                "capacity": 120,
                "delay_ticks": 0,
                "cost_units": 1,
                "payload": {
                    "schema_version": "1.0.0",
                    "edge_kind": "conductor",
                    "length": 400,
                    "resistance_proxy": 8,
                    "capacity_rating": 120,
                    "spec_id": None,
                    "deterministic_fingerprint": "",
                    "extensions": {"cross_shard_boundary": True},
                },
                "extensions": {"cross_shard_boundary": True},
            }
        ],
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context,
        base_state,
        law_profile,
        model_binding_rows,
        policy_context,
    )

    state = base_state(current_tick=17)
    state["power_network_graphs"] = [_invalid_cross_shard_graph()]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=60, motor_demand_p=40, motor_pf_permille=900)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec5.shard.boundary.invalid.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.shard.invalid"},
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "invalid cross-shard boundary graph should be refused"}
    error_row = dict(result.get("error") or {})
    if not error_row:
        error_rows = [dict(row) for row in list(result.get("errors") or []) if isinstance(row, dict)]
        if error_rows:
            error_row = dict(error_rows[0])
    if not error_row:
        error_row = dict(result.get("refusal") or {})
    code = str(error_row.get("code", error_row.get("reason_code", ""))).strip()
    if code != "refusal.elec.shard_boundary_invalid":
        return {"status": "fail", "message": "unexpected refusal code for shard boundary validation: {}".format(code)}
    return {"status": "pass", "message": "ELEC-5 shard boundary rules enforced deterministically"}
