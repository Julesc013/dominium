"""STRICT test: process.spec_check_compliance produces deterministic results."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.specs.compliance_result_deterministic"
TEST_TAGS = ["strict", "specs", "determinism"]


def _base_state():
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["installed_structure_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "structure.spec.alpha",
            "project_id": "",
            "ag_id": "",
            "site_ref": "",
            "installed_node_states": [],
            "maintenance_backlog": {},
            "extensions": {},
        }
    ]
    return state


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


def _inspection_snapshot() -> dict:
    return {
        "schema_version": "1.0.0",
        "snapshot_id": "snapshot.spec.det.001",
        "tick": 0,
        "target_id": "structure.spec.alpha",
        "summary_sections": {
            "section.interior.layout": {
                "section_id": "section.interior.layout",
                "data": {"min_clearance_mm": 4600},
            },
            "section.interior.connectivity_summary": {
                "section_id": "section.interior.connectivity_summary",
                "data": {"min_curvature_radius_mm": 220000},
            },
            "section.failure_risk_summary": {
                "section_id": "section.failure_risk_summary",
                "data": {"max_speed_kph": 140},
            },
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    intent = {
        "intent_id": "intent.spec.compliance.det.001",
        "process_id": "process.spec_check_compliance",
        "inputs": {
            "spec_id": "spec.track.standard_gauge.v1",
            "target_kind": "structure",
            "target_id": "structure.spec.alpha",
            "strict": False,
            "inspection_snapshot": _inspection_snapshot(),
        },
    }
    law = _law_profile()
    authority = authority_context(["entitlement.inspect"], privilege_level="observer")
    policy = policy_context()

    state_a = _base_state()
    state_b = _base_state()
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
        return {"status": "fail", "message": "spec_check_compliance deterministic fixture refused unexpectedly"}

    first_result = dict(first.get("compliance_result") or {})
    second_result = dict(second.get("compliance_result") or {})
    if first_result != second_result:
        return {"status": "fail", "message": "compliance_result drifted across equivalent executions"}
    if str(first_result.get("overall_grade", "")).strip() not in {"pass", "warn", "fail"}:
        return {"status": "fail", "message": "compliance_result missing deterministic overall_grade token"}
    if not str(first_result.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "compliance_result missing deterministic_fingerprint"}

    first_rows = list(state_a.get("spec_compliance_results") or [])
    second_rows = list(state_b.get("spec_compliance_results") or [])
    if first_rows != second_rows:
        return {"status": "fail", "message": "spec_compliance_results state drifted for equivalent compliance checks"}

    return {"status": "pass", "message": "spec compliance results deterministic for equivalent inputs"}

