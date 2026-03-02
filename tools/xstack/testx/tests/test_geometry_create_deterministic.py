"""FAST test: process.geometry_create is deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.geometry_create_deterministic"
TEST_TAGS = ["fast", "mobility", "geometry", "determinism"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(["process.geometry_create"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.geometry_create"] = "entitlement.control.admin"
    privileges["process.geometry_create"] = "operator"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _intent() -> dict:
    return {
        "intent_id": "intent.mob.geometry.create.det.001",
        "process_id": "process.geometry_create",
        "inputs": {
            "geometry_type_id": "geo.spline1D",
            "parent_spatial_id": "spatial.test.geometry",
            "formalization_id": "formalization.test.geometry",
            "candidate_id": "candidate.test.geometry",
            "created_tick_bucket": 0,
            "snap_policy_id": "snap.none",
            "parameters": {
                "control_points_mm": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 2000, "y": 400, "z": 0},
                    {"x": 5000, "y": 800, "z": 0},
                ],
                "gauge_mm": 1435,
            },
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, base_state, policy_context

    law = _law_profile()
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    policy = policy_context()
    intent = _intent()

    state_a = base_state()
    state_b = base_state()
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
        return {"status": "fail", "message": "geometry_create refused in deterministic fixture"}
    if str(first.get("geometry_id", "")).strip() != str(second.get("geometry_id", "")).strip():
        return {"status": "fail", "message": "geometry_id drifted across equivalent geometry_create runs"}
    if list(state_a.get("guide_geometries") or []) != list(state_b.get("guide_geometries") or []):
        return {"status": "fail", "message": "guide_geometries drifted for equivalent geometry_create runs"}
    return {"status": "pass", "message": "geometry_create deterministic for equivalent inputs"}
