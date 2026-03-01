"""STRICT test: SPEC runtime remains lawful when no spec packs are available."""

from __future__ import annotations

import copy
import sys
from unittest.mock import patch


TEST_ID = "testx.specs.no_spec_packs_null_boot_ok"
TEST_TAGS = ["strict", "specs", "null_boot"]


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

    from tools.xstack.sessionx import process_runtime
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    execute_intent = process_runtime.execute_intent
    default_pack_suffix = "packs/specs/specs.default.realistic.m1/data/spec_sheets.json"

    intent = {
        "intent_id": "intent.spec.null_pack.001",
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
    state = _base_state()

    original_isfile = process_runtime.os.path.isfile

    def _patched_isfile(path: str) -> bool:
        normalized = str(path).replace("\\", "/")
        if normalized.endswith(default_pack_suffix):
            return False
        return bool(original_isfile(path))

    with patch("tools.xstack.sessionx.process_runtime.os.path.isfile", side_effect=_patched_isfile):
        result = execute_intent(
            state=state,
            intent=copy.deepcopy(intent),
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )

    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "expected refusal when no spec packs are available for requested spec_id"}
    refusal = dict(result.get("refusal") or {})
    reason = str(refusal.get("reason_code", "")).strip()
    if reason != "refusal.spec.unknown_spec_id":
        return {"status": "fail", "message": "unexpected refusal code without spec packs: {}".format(reason or "<missing>")}
    if list(state.get("spec_bindings") or []):
        return {"status": "fail", "message": "spec bindings mutated despite unknown spec_id under no-pack scenario"}
    return {"status": "pass", "message": "no-spec-pack runtime path remains deterministic and lawfully refuses unknown specs"}

