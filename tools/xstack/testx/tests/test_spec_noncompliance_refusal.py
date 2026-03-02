"""FAST test: require_spec enforces mobility spec-noncompliance refusal."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.spec_noncompliance_refusal"
TEST_TAGS = ["fast", "mobility", "network", "spec", "refusal"]


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
    from src.mobility.geometry import build_guide_geometry, build_junction
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["formalization_states"] = [
        {
            "schema_version": "1.0.0",
            "formalization_id": "formalization.mob.spec.refusal",
            "target_kind": "track",
            "target_context_id": "spatial.mob.spec.refusal",
            "state": "formal",
            "raw_sources": ["part.track.no_spec"],
            "inferred_artifact_ref": None,
            "formal_artifact_ref": "geometry.mob.spec.no_spec",
            "network_graph_ref": None,
            "spec_id": None,
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["guide_geometries"] = [
        build_guide_geometry(
            geometry_id="geometry.mob.spec.no_spec",
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.spec.refusal",
            spec_id=None,
            parameters={
                "control_points_mm": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 3000, "y": 0, "z": 0},
                ]
            },
            junction_refs=["junction.mob.spec.start", "junction.mob.spec.end"],
            extensions={},
        )
    ]
    state["mobility_junctions"] = [
        build_junction(
            junction_id="junction.mob.spec.start",
            parent_spatial_id="spatial.mob.spec.refusal",
            connected_geometry_ids=["geometry.mob.spec.no_spec"],
            junction_type_id="junc.endpoint",
            extensions={},
        ),
        build_junction(
            junction_id="junction.mob.spec.end",
            parent_spatial_id="spatial.mob.spec.refusal",
            connected_geometry_ids=["geometry.mob.spec.no_spec"],
            junction_type_id="junc.endpoint",
            extensions={},
        ),
    ]
    return state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    state = _seed_state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.spec.refusal.001",
            "process_id": "process.mobility_network_create_from_formalization",
            "inputs": {
                "formalization_id": "formalization.mob.spec.refusal",
                "require_spec": True,
            },
        },
        law_profile=_law_profile(),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) == "complete":
        return {"status": "fail", "message": "expected spec-noncompliance refusal but process completed"}
    refusal = dict(result.get("refusal") or {})
    if str(refusal.get("reason_code", "")).strip() != "refusal.mob.spec_noncompliant":
        return {"status": "fail", "message": "expected refusal.mob.spec_noncompliant for require_spec violation"}
    return {"status": "pass", "message": "spec noncompliance refusal emitted deterministically"}
