"""STRICT test: formalization acceptance creates canonical GuideGeometry artifacts."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.formalization_accept_creates_geometry"
TEST_TAGS = ["strict", "mobility", "formalization", "geometry"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(["process.formalization_infer", "process.formalization_accept_candidate"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.formalization_infer"] = "entitlement.inspect"
    privileges["process.formalization_infer"] = "observer"
    entitlements["process.formalization_accept_candidate"] = "entitlement.control.admin"
    privileges["process.formalization_accept_candidate"] = "operator"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _infer(state: dict, law: dict, authority: dict, policy: dict) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.form.infer.001",
            "process_id": "process.formalization_infer",
            "inputs": {
                "formalization_id": "formalization.mob.accept.alpha",
                "target_kind": "track",
                "target_context_id": "spatial.mobility.alpha",
                "raw_sources": ["part.track.a", "part.track.b", "part.track.c"],
                "max_search_cost_units": 8,
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

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, base_state, policy_context

    state = base_state()
    law = _law_profile()
    policy = policy_context()
    infer = _infer(
        state,
        law=law,
        authority=authority_context(["entitlement.inspect"], privilege_level="observer"),
        policy=policy,
    )
    if str(infer.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization infer failed in GuideGeometry accept fixture"}
    candidates = [dict(item) for item in list(infer.get("candidates") or []) if isinstance(item, dict)]
    candidate_id = str((dict(candidates[0]) if candidates else {}).get("candidate_id", "")).strip()
    if not candidate_id:
        return {"status": "fail", "message": "missing candidate_id for formalization acceptance fixture"}

    accept = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.form.accept.001",
            "process_id": "process.formalization_accept_candidate",
            "inputs": {
                "formalization_id": "formalization.mob.accept.alpha",
                "candidate_id": candidate_id,
                "confirmed": True,
                "spec_id": "spec.track.standard_gauge.v1",
                "requested_speed_kph": 140,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(accept.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization acceptance refused unexpectedly"}

    geometry_id = str(accept.get("geometry_id", "")).strip()
    if not geometry_id:
        return {"status": "fail", "message": "formalization acceptance did not return geometry_id"}
    guide_rows = [dict(item) for item in list(state.get("guide_geometries") or []) if isinstance(item, dict)]
    if not any(str(row.get("geometry_id", "")).strip() == geometry_id for row in guide_rows):
        return {"status": "fail", "message": "accepted candidate did not persist GuideGeometry row"}

    formal_rows = [dict(item) for item in list(state.get("formalization_states") or []) if isinstance(item, dict)]
    formal_row = next(
        (row for row in formal_rows if str(row.get("formalization_id", "")).strip() == "formalization.mob.accept.alpha"),
        {},
    )
    if str(formal_row.get("formal_artifact_ref", "")).strip() != geometry_id:
        return {"status": "fail", "message": "formal_artifact_ref was not bound to created geometry_id"}

    candidate_rows = [dict(item) for item in list(state.get("geometry_candidates") or []) if isinstance(item, dict)]
    if not any(str(row.get("candidate_id", "")).strip() == candidate_id for row in candidate_rows):
        return {"status": "fail", "message": "geometry_candidates missing accepted candidate linkage"}
    return {"status": "pass", "message": "formalization acceptance created canonical GuideGeometry artifact"}
