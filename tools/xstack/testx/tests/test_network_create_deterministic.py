"""FAST test: mobility network creation from formalization is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.network_create_deterministic"
TEST_TAGS = ["fast", "mobility", "network", "determinism"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(["process.mobility_network_create_from_formalization"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.mobility_network_create_from_formalization"] = "entitlement.control.admin"
    privileges["process.mobility_network_create_from_formalization"] = "operator"
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
            "formalization_id": "formalization.mob.net.det",
            "target_kind": "track",
            "target_context_id": "spatial.mob.net.det",
            "state": "formal",
            "raw_sources": ["part.track.det.1"],
            "inferred_artifact_ref": None,
            "formal_artifact_ref": "geometry.mob.det.main",
            "network_graph_ref": None,
            "spec_id": "spec.track.standard_gauge.v1",
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["guide_geometries"] = [
        build_guide_geometry(
            geometry_id="geometry.mob.det.main",
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.net.det",
            spec_id="spec.track.standard_gauge.v1",
            parameters={
                "control_points_mm": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 6000, "y": 0, "z": 0},
                ]
            },
            junction_refs=["junction.mob.det.start", "junction.mob.det.end"],
            extensions={},
        )
    ]
    state["mobility_junctions"] = [
        build_junction(
            junction_id="junction.mob.det.start",
            parent_spatial_id="spatial.mob.net.det",
            connected_geometry_ids=["geometry.mob.det.main"],
            junction_type_id="junc.endpoint",
            extensions={},
        ),
        build_junction(
            junction_id="junction.mob.det.end",
            parent_spatial_id="spatial.mob.net.det",
            connected_geometry_ids=["geometry.mob.det.main"],
            junction_type_id="junc.endpoint",
            extensions={},
        ),
    ]
    state["geometry_derived_metrics"] = [
        {
            "schema_version": "1.0.0",
            "geometry_id": "geometry.mob.det.main",
            "length_mm": 6000,
            "curvature_bands": [],
            "clearance_envelope": {},
            "degraded": False,
            "metric_cost_units": 1,
            "geometry_hash": "det",
            "deterministic_fingerprint": "det",
            "extensions": {},
        }
    ]
    return state


def _intent() -> dict:
    return {
        "intent_id": "intent.mob.network.det.001",
        "process_id": "process.mobility_network_create_from_formalization",
        "inputs": {
            "formalization_id": "formalization.mob.net.det",
            "promote_state": False,
            "require_spec": True,
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    law = _law_profile()
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    policy = policy_context()
    intent = _intent()

    state_a = _seed_state()
    state_b = _seed_state()
    first = execute_intent(
        state=state_a,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = execute_intent(
        state=state_b,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "mobility network creation refused in deterministic fixture"}
    if str(first.get("network_graph_ref", "")).strip() != str(second.get("network_graph_ref", "")).strip():
        return {"status": "fail", "message": "graph_id drifted across equivalent mobility network creates"}
    if list(state_a.get("network_graphs") or []) != list(state_b.get("network_graphs") or []):
        return {"status": "fail", "message": "network_graph rows drifted across equivalent mobility network creates"}
    if list(state_a.get("mobility_network_bindings") or []) != list(state_b.get("mobility_network_bindings") or []):
        return {"status": "fail", "message": "mobility_network_binding rows drifted across equivalent runs"}
    return {"status": "pass", "message": "mobility network creation deterministic for equivalent formalization inputs"}
