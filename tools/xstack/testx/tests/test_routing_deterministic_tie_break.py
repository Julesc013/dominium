"""FAST test: mobility route query uses deterministic tie-break on equivalent paths."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.routing_deterministic_tie_break"
TEST_TAGS = ["fast", "mobility", "routing", "determinism"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(["process.mobility_route_query"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.mobility_route_query"] = "entitlement.inspect"
    privileges["process.mobility_route_query"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _seed_state() -> dict:
    from core.graph.network_graph_engine import normalize_network_graph
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["network_graphs"] = [
        normalize_network_graph(
            {
                "schema_version": "1.0.0",
                "graph_id": "graph.mob.tie_break.alpha",
                "node_type_schema_id": "dominium.schema.mobility.mobility_node_payload.v1",
                "edge_type_schema_id": "dominium.schema.mobility.mobility_edge_payload.v1",
                "payload_schema_versions": {
                    "dominium.schema.mobility.mobility_node_payload.v1": "1.0.0",
                    "dominium.schema.mobility.mobility_edge_payload.v1": "1.0.0",
                },
                "validation_mode": "strict",
                "nodes": [
                    {"schema_version": "1.0.0", "node_id": "node.mob.a", "node_type_id": "node.mobility.endpoint", "payload": {"node_kind": "endpoint"}, "tags": [], "extensions": {}},
                    {"schema_version": "1.0.0", "node_id": "node.mob.b", "node_type_id": "node.mobility.waypoint", "payload": {"node_kind": "waypoint"}, "tags": [], "extensions": {}},
                    {"schema_version": "1.0.0", "node_id": "node.mob.c", "node_type_id": "node.mobility.waypoint", "payload": {"node_kind": "waypoint"}, "tags": [], "extensions": {}},
                    {"schema_version": "1.0.0", "node_id": "node.mob.d", "node_type_id": "node.mobility.endpoint", "payload": {"node_kind": "endpoint"}, "tags": [], "extensions": {}},
                ],
                "edges": [
                    {"schema_version": "1.0.0", "edge_id": "edge.path.a_b", "from_node_id": "node.mob.a", "to_node_id": "node.mob.b", "edge_type_id": "edge.mobility.track", "capacity": None, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "payload": {"edge_kind": "track", "guide_geometry_id": "g1", "spec_id": "spec.track.standard_gauge.v1"}, "extensions": {}},
                    {"schema_version": "1.0.0", "edge_id": "edge.path.a_c", "from_node_id": "node.mob.a", "to_node_id": "node.mob.c", "edge_type_id": "edge.mobility.track", "capacity": None, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "payload": {"edge_kind": "track", "guide_geometry_id": "g2", "spec_id": "spec.track.standard_gauge.v1"}, "extensions": {}},
                    {"schema_version": "1.0.0", "edge_id": "edge.path.b_d", "from_node_id": "node.mob.b", "to_node_id": "node.mob.d", "edge_type_id": "edge.mobility.track", "capacity": None, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "payload": {"edge_kind": "track", "guide_geometry_id": "g3", "spec_id": "spec.track.standard_gauge.v1"}, "extensions": {}},
                    {"schema_version": "1.0.0", "edge_id": "edge.path.c_d", "from_node_id": "node.mob.c", "to_node_id": "node.mob.d", "edge_type_id": "edge.mobility.track", "capacity": None, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "payload": {"edge_kind": "track", "guide_geometry_id": "g4", "spec_id": "spec.track.standard_gauge.v1"}, "extensions": {}},
                ],
                "deterministic_routing_policy_id": "route.shortest_delay",
                "extensions": {},
            }
        )
    ]
    return state


def _route(state: dict, law: dict, authority: dict, policy: dict, intent_id: str) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": intent_id,
            "process_id": "process.mobility_route_query",
            "inputs": {
                "graph_id": "graph.mob.tie_break.alpha",
                "from_node_id": "node.mob.a",
                "to_node_id": "node.mob.d",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    law = _law_profile()
    authority = authority_context(["entitlement.inspect"], privilege_level="observer")
    policy = policy_context()

    first_state = _seed_state()
    second_state = _seed_state()
    first = _route(first_state, law, authority, policy, "intent.mob.route.tie.001")
    second = _route(second_state, law, authority, policy, "intent.mob.route.tie.002")

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "mobility route query failed in tie-break fixture"}

    path_a = [str(item).strip() for item in list((dict(first.get("route_result") or {})).get("path_edge_ids") or []) if str(item).strip()]
    path_b = [str(item).strip() for item in list((dict(second.get("route_result") or {})).get("path_edge_ids") or []) if str(item).strip()]
    if path_a != path_b:
        return {"status": "fail", "message": "equivalent route queries produced different path edge ordering"}
    expected = ["edge.path.a_b", "edge.path.b_d"]
    if path_a != expected:
        return {"status": "fail", "message": "tie-break path does not match deterministic lexicographic expectation"}
    return {"status": "pass", "message": "mobility routing tie-break is deterministic"}
