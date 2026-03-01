"""STRICT test: process.spec_apply_to_target is deterministic and process-only."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.specs.apply_deterministic"
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

    law = law_profile(["process.spec_apply_to_target"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.spec_apply_to_target"] = "entitlement.control.admin"
    privileges["process.spec_apply_to_target"] = "operator"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    intent = {
        "intent_id": "intent.spec.apply.det.001",
        "process_id": "process.spec_apply_to_target",
        "inputs": {
            "spec_id": "spec.track.standard_gauge.v1",
            "target_kind": "structure",
            "target_id": "structure.spec.alpha",
        },
    }
    law = _law_profile()
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
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
        return {"status": "fail", "message": "spec_apply deterministic fixture refused unexpectedly"}

    comparable_keys = (
        "binding_id",
        "spec_id",
        "target_kind",
        "target_id",
        "annotated_target_rows",
    )
    first_summary = dict((key, first.get(key)) for key in comparable_keys)
    second_summary = dict((key, second.get(key)) for key in comparable_keys)
    if first_summary != second_summary:
        return {"status": "fail", "message": "spec apply metadata drifted across equivalent executions"}

    first_bindings = list(state_a.get("spec_bindings") or [])
    second_bindings = list(state_b.get("spec_bindings") or [])
    if first_bindings != second_bindings:
        return {"status": "fail", "message": "spec_bindings state drifted for equivalent apply intent"}

    first_structures = list(state_a.get("installed_structure_instances") or [])
    second_structures = list(state_b.get("installed_structure_instances") or [])
    if first_structures != second_structures:
        return {"status": "fail", "message": "structure annotation drifted for equivalent spec apply intent"}

    return {"status": "pass", "message": "spec apply process deterministic and target annotation stable"}

