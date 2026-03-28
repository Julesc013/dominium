"""STRICT test: geometry-targeted spec compliance checks remain deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.spec_compliance_check_deterministic"
TEST_TAGS = ["strict", "mobility", "geometry", "specs", "determinism"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(["process.spec_check_compliance"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.spec_check_compliance"] = "entitlement.inspect"
    privileges["process.spec_check_compliance"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _state_with_geometry() -> dict:
    from mobility.geometry import build_geometry_metric_row, build_guide_geometry
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    geometry_row = build_guide_geometry(
        geometry_id="geometry.spec.det.alpha",
        geometry_type_id="geo.spline1D",
        parent_spatial_id="spatial.test.geometry",
        spec_id="spec.track.standard_gauge.v1",
        parameters={
            "control_points_mm": [
                {"x": 0, "y": 0, "z": 0},
                {"x": 5000, "y": 800, "z": 0},
                {"x": 10000, "y": 1800, "z": 0},
            ],
            "gauge_mm": 1435,
        },
        bounds=None,
        junction_refs=[],
        extensions={},
    )
    metric_row = build_geometry_metric_row(
        geometry_row=geometry_row,
        current_tick=0,
        max_cost_units=3,
        cost_units_per_metric=1,
    )
    state["guide_geometries"] = [dict(geometry_row)]
    state["geometry_derived_metrics"] = [dict(metric_row)]
    return state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    intent = {
        "intent_id": "intent.mob.spec.geometry.det.001",
        "process_id": "process.spec_check_compliance",
        "inputs": {
            "spec_id": "spec.track.standard_gauge.v1",
            "target_kind": "geometry",
            "target_id": "geometry.spec.det.alpha",
            "strict": False,
            "requested_speed_kph": 180,
        },
    }
    law = _law_profile()
    authority = authority_context(["entitlement.inspect"], privilege_level="observer")
    policy = policy_context()

    state_a = _state_with_geometry()
    state_b = _state_with_geometry()
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
        return {"status": "fail", "message": "geometry spec compliance fixture refused unexpectedly"}
    first_result = dict(first.get("compliance_result") or {})
    second_result = dict(second.get("compliance_result") or {})
    if first_result != second_result:
        return {"status": "fail", "message": "geometry compliance result drifted across equivalent executions"}
    check_ids = sorted(
        str(row.get("check_id", "")).strip()
        for row in list(first_result.get("check_results") or [])
        if isinstance(row, dict)
    )
    if "check.geometry.gauge_width_stub" not in check_ids:
        return {"status": "fail", "message": "geometry compliance result missing gauge_width_stub check"}
    return {"status": "pass", "message": "geometry spec compliance deterministic with gauge/curvature inputs"}
