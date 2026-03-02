"""FAST test: GuideGeometry metric budget degradation is explicit and deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.budget_degrade_geometry_metrics"
TEST_TAGS = ["fast", "mobility", "geometry", "budget", "degrade"]


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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, base_state, policy_context

    state = base_state()
    law = _law_profile()
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    policy = policy_context()
    intent = {
        "intent_id": "intent.mob.geometry.budget.001",
        "process_id": "process.geometry_create",
        "inputs": {
            "geometry_type_id": "geo.spline1D",
            "parent_spatial_id": "spatial.test.geometry",
            "formalization_id": "formalization.budget.geometry",
            "candidate_id": "candidate.budget.geometry",
            "created_tick_bucket": 0,
            "snap_policy_id": "snap.none",
            "parameters": {
                "control_points_mm": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 1500, "y": 200, "z": 0},
                    {"x": 3200, "y": 380, "z": 0},
                    {"x": 5200, "y": 620, "z": 0},
                    {"x": 8000, "y": 920, "z": 0},
                ],
                "gauge_mm": 1435,
            },
            "max_metric_cost_units": 1,
            "cost_units_per_metric": 1,
        },
    }
    result = execute_intent(
        state=state,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "geometry budget degrade fixture refused unexpectedly"}
    metric_row = dict(result.get("metric_row") or {})
    if not bool(result.get("metrics_degraded", False)) or not bool(metric_row.get("degraded", False)):
        return {"status": "fail", "message": "geometry metric budget degradation was not surfaced"}
    decision_rows = [dict(item) for item in list(state.get("fidelity_decision_entries") or []) if isinstance(item, dict)]
    has_metric_budget_decision = any(
        str(row.get("downgrade_reason", "")).strip() == "degrade.geometry.metrics_budget"
        for row in decision_rows
    )
    if not has_metric_budget_decision:
        return {"status": "fail", "message": "missing fidelity decision entry for geometry metric budget degradation"}
    return {"status": "pass", "message": "geometry metric budget degradation is explicit and deterministic"}
