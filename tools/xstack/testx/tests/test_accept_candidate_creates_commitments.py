"""STRICT test: FORM-1 accept candidate creates commitments and formal state."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.infrastructure.formalization.accept_candidate_creates_commitments"
TEST_TAGS = ["strict", "infrastructure", "formalization", "commitments"]


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
            "intent_id": "intent.form.accept.infer.001",
            "process_id": "process.formalization_infer",
            "inputs": {
                "formalization_id": "formalization.accept.alpha",
                "target_kind": "track",
                "target_context_id": "assembly.structure_instance.alpha",
                "raw_sources": ["part.a", "part.b", "part.c"],
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
    infer_authority = authority_context(["entitlement.inspect"], privilege_level="observer")
    infer = _infer(state, law=law, authority=infer_authority, policy=policy)
    if str(infer.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization inference fixture failed before accept"}
    candidates = [dict(item) for item in list(infer.get("candidates") or []) if isinstance(item, dict)]
    if not candidates:
        return {"status": "fail", "message": "no candidates returned for acceptance test"}
    candidate_id = str(candidates[0].get("candidate_id", "")).strip()
    if not candidate_id:
        return {"status": "fail", "message": "candidate missing deterministic candidate_id"}

    accept = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.accept.001",
            "process_id": "process.formalization_accept_candidate",
            "inputs": {
                "formalization_id": "formalization.accept.alpha",
                "candidate_id": candidate_id,
                "confirmed": True,
                "requires_physical_upgrade": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(accept.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization accept candidate refused unexpectedly"}
    commitment_id = str(accept.get("commitment_id", "")).strip()
    if not commitment_id:
        return {"status": "fail", "message": "accept process missing commitment_id"}

    commitment_rows = [dict(item) for item in list(state.get("material_commitments") or []) if isinstance(item, dict)]
    matched = {}
    for row in commitment_rows:
        if str(row.get("commitment_id", "")).strip() != commitment_id:
            continue
        matched = dict(row)
        break
    if not matched:
        return {"status": "fail", "message": "accept process did not persist expected commitment row"}
    ext = dict(matched.get("extensions") or {})
    if str(ext.get("formalization_id", "")).strip() != "formalization.accept.alpha":
        return {"status": "fail", "message": "commitment row missing formalization_id linkage"}

    state_rows = [dict(item) for item in list(state.get("formalization_states") or []) if isinstance(item, dict)]
    state_row = {}
    for row in state_rows:
        if str(row.get("formalization_id", "")).strip() == "formalization.accept.alpha":
            state_row = dict(row)
            break
    if str(state_row.get("state", "")).strip() != "formal":
        return {"status": "fail", "message": "formalization state did not transition to formal after acceptance"}
    return {"status": "pass", "message": "accept candidate created commitment and formal state"}

