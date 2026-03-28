"""STRICT test: switch state transitions gate route availability deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.switch_state_changes_route_availability"
TEST_TAGS = ["strict", "mobility", "network", "switch", "routing"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(
        [
            "process.mobility_network_create_from_formalization",
            "process.switch_set_state",
            "process.mobility_route_query",
        ]
    )
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.mobility_network_create_from_formalization"] = "entitlement.control.admin"
    privileges["process.mobility_network_create_from_formalization"] = "operator"
    entitlements["process.switch_set_state"] = "entitlement.control.admin"
    privileges["process.switch_set_state"] = "operator"
    entitlements["process.mobility_route_query"] = "entitlement.inspect"
    privileges["process.mobility_route_query"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _seed_state() -> dict:
    from mobility.geometry import build_guide_geometry, build_junction
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["formalization_states"] = [
        {
            "schema_version": "1.0.0",
            "formalization_id": "formalization.mob.switch.alpha",
            "target_kind": "track",
            "target_context_id": "spatial.mob.switch.alpha",
            "state": "formal",
            "raw_sources": ["part.switch.alpha"],
            "inferred_artifact_ref": None,
            "formal_artifact_ref": "geometry.mob.switch.a",
            "network_graph_ref": None,
            "spec_id": "spec.track.standard_gauge.v1",
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["guide_geometries"] = [
        build_guide_geometry(
            geometry_id="geometry.mob.switch.a",
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.switch.alpha",
            spec_id="spec.track.standard_gauge.v1",
            parameters={"control_points_mm": [{"x": 0, "y": 0, "z": 0}, {"x": 3000, "y": 0, "z": 0}]},
            junction_refs=["junction.mob.switch.0_core", "junction.mob.switch.1_a_end"],
            extensions={},
        ),
        build_guide_geometry(
            geometry_id="geometry.mob.switch.b",
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.switch.alpha",
            spec_id="spec.track.standard_gauge.v1",
            parameters={"control_points_mm": [{"x": 0, "y": 0, "z": 0}, {"x": 3000, "y": 1200, "z": 0}]},
            junction_refs=["junction.mob.switch.0_core", "junction.mob.switch.2_b_end"],
            extensions={},
        ),
    ]
    state["mobility_junctions"] = [
        build_junction(
            junction_id="junction.mob.switch.0_core",
            parent_spatial_id="spatial.mob.switch.alpha",
            connected_geometry_ids=["geometry.mob.switch.a", "geometry.mob.switch.b"],
            junction_type_id="junc.switch",
            state_machine_id="state_machine.mob.switch.alpha",
            extensions={},
        ),
        build_junction(
            junction_id="junction.mob.switch.1_a_end",
            parent_spatial_id="spatial.mob.switch.alpha",
            connected_geometry_ids=["geometry.mob.switch.a"],
            junction_type_id="junc.endpoint",
            extensions={},
        ),
        build_junction(
            junction_id="junction.mob.switch.2_b_end",
            parent_spatial_id="spatial.mob.switch.alpha",
            connected_geometry_ids=["geometry.mob.switch.b"],
            junction_type_id="junc.endpoint",
            extensions={},
        ),
    ]
    state["geometry_derived_metrics"] = [
        {
            "schema_version": "1.0.0",
            "geometry_id": "geometry.mob.switch.a",
            "length_mm": 3000,
            "curvature_bands": [],
            "clearance_envelope": {},
            "degraded": False,
            "metric_cost_units": 1,
            "geometry_hash": "switch_a",
            "deterministic_fingerprint": "switch_a",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "geometry_id": "geometry.mob.switch.b",
            "length_mm": 3000,
            "curvature_bands": [],
            "clearance_envelope": {},
            "degraded": False,
            "metric_cost_units": 1,
            "geometry_hash": "switch_b",
            "deterministic_fingerprint": "switch_b",
            "extensions": {},
        },
    ]
    return state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    law = _law_profile()
    authority = authority_context(["entitlement.control.admin", "entitlement.inspect"], privilege_level="operator")
    policy = policy_context()
    state = _seed_state()

    create = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.switch.create.001",
            "process_id": "process.mobility_network_create_from_formalization",
            "inputs": {"formalization_id": "formalization.mob.switch.alpha", "promote_state": False},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(create.get("result", "")) != "complete":
        return {"status": "fail", "message": "mobility network creation failed in switch fixture"}

    graph_id = str(create.get("network_graph_ref", "")).strip()
    graph_row = next(
        (
            dict(item)
            for item in list(state.get("network_graphs") or [])
            if isinstance(item, dict) and str(item.get("graph_id", "")).strip() == graph_id
        ),
        {},
    )
    if not graph_row:
        return {"status": "fail", "message": "missing graph row after mobility network creation"}

    switch_node_id = ""
    for node in list(graph_row.get("nodes") or []):
        if not isinstance(node, dict):
            continue
        payload = dict(node.get("payload") or {})
        if str(payload.get("node_kind", "")).strip() == "switch":
            switch_node_id = str(node.get("node_id", "")).strip()
            break
    if not switch_node_id:
        return {"status": "fail", "message": "expected switch node in mobility graph"}

    outgoing_edges = sorted(
        [
            dict(edge)
            for edge in list(graph_row.get("edges") or [])
            if isinstance(edge, dict) and str(edge.get("from_node_id", "")).strip() == switch_node_id
        ],
        key=lambda edge: str(edge.get("edge_id", "")),
    )
    if len(outgoing_edges) < 2:
        return {"status": "fail", "message": "switch fixture requires two outgoing edges"}

    machine_rows = sorted(
        [dict(item) for item in list(state.get("mobility_switch_state_machines") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("machine_id", "")),
    )
    if not machine_rows:
        return {"status": "fail", "message": "switch state machine missing after network creation"}
    machine_id = str(machine_rows[0].get("machine_id", "")).strip()
    active_edge_id = str(machine_rows[0].get("state_id", "")).strip()
    inactive_edge = next(
        (
            edge
            for edge in outgoing_edges
            if str(edge.get("edge_id", "")).strip() and str(edge.get("edge_id", "")).strip() != active_edge_id
        ),
        {},
    )
    if not inactive_edge:
        return {"status": "fail", "message": "unable to find alternate outgoing edge for switch test"}
    inactive_edge_id = str(inactive_edge.get("edge_id", "")).strip()
    inactive_target_node = str(inactive_edge.get("to_node_id", "")).strip()
    if (not inactive_edge_id) or (not inactive_target_node):
        return {"status": "fail", "message": "invalid alternate switch edge for route availability test"}

    blocked_route = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.switch.route.blocked.001",
            "process_id": "process.mobility_route_query",
            "inputs": {
                "graph_id": graph_id,
                "from_node_id": switch_node_id,
                "to_node_id": inactive_target_node,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(blocked_route.get("result", "")) == "complete":
        return {"status": "fail", "message": "route unexpectedly available before switch transition"}
    refusal = dict(blocked_route.get("refusal") or {})
    if str(refusal.get("reason_code", "")).strip() != "refusal.mob.no_route":
        return {"status": "fail", "message": "expected refusal.mob.no_route before switch transition"}

    switched = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.switch.set.001",
            "process_id": "process.switch_set_state",
            "inputs": {
                "machine_id": machine_id,
                "target_edge_id": inactive_edge_id,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(switched.get("result", "")) != "complete":
        return {"status": "fail", "message": "switch_set_state refused for valid transition"}

    opened_route = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.switch.route.opened.001",
            "process_id": "process.mobility_route_query",
            "inputs": {
                "graph_id": graph_id,
                "from_node_id": switch_node_id,
                "to_node_id": inactive_target_node,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(opened_route.get("result", "")) != "complete":
        return {"status": "fail", "message": "route should be available after switch transition"}
    route_result = dict(opened_route.get("route_result") or {})
    path_edge_ids = [str(item).strip() for item in list(route_result.get("path_edge_ids") or []) if str(item).strip()]
    if not path_edge_ids or path_edge_ids[0] != inactive_edge_id:
        return {"status": "fail", "message": "route path does not reflect switched active edge"}
    return {"status": "pass", "message": "switch state transitions deterministically gate route availability"}
