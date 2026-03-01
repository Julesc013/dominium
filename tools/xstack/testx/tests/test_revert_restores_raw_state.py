"""STRICT test: FORM-1 revert returns lifecycle to raw and keeps raw_sources."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.infrastructure.formalization.revert_restores_raw_state"
TEST_TAGS = ["strict", "infrastructure", "formalization", "revert"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(
        [
            "process.formalization_infer",
            "process.formalization_accept_candidate",
            "process.formalization_promote_networked",
            "process.formalization_revert",
        ]
    )
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.formalization_infer"] = "entitlement.inspect"
    privileges["process.formalization_infer"] = "observer"
    entitlements["process.formalization_accept_candidate"] = "entitlement.control.admin"
    privileges["process.formalization_accept_candidate"] = "operator"
    entitlements["process.formalization_promote_networked"] = "entitlement.control.admin"
    privileges["process.formalization_promote_networked"] = "operator"
    entitlements["process.formalization_revert"] = "entitlement.control.admin"
    privileges["process.formalization_revert"] = "operator"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _state_row(state: dict, formalization_id: str) -> dict:
    for row in list(state.get("formalization_states") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("formalization_id", "")).strip() == formalization_id:
            return dict(row)
    return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, base_state, policy_context

    state = base_state()
    law = _law_profile()
    policy = policy_context()
    formalization_id = "formalization.revert.alpha"
    raw_sources = ["part.a", "part.b", "part.c"]

    infer = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.revert.infer.001",
            "process_id": "process.formalization_infer",
            "inputs": {
                "formalization_id": formalization_id,
                "target_kind": "track",
                "target_context_id": "assembly.structure_instance.alpha",
                "raw_sources": list(raw_sources),
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.inspect"], privilege_level="observer"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(infer.get("result", "")) != "complete":
        return {"status": "fail", "message": "infer failed in revert fixture"}
    candidate_id = str((dict((list(infer.get("candidates") or []) or [{}])[0])).get("candidate_id", "")).strip()
    if not candidate_id:
        return {"status": "fail", "message": "missing candidate_id in revert fixture"}

    accept = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.revert.accept.001",
            "process_id": "process.formalization_accept_candidate",
            "inputs": {
                "formalization_id": formalization_id,
                "candidate_id": candidate_id,
                "confirmed": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(accept.get("result", "")) != "complete":
        return {"status": "fail", "message": "accept failed in revert fixture"}

    promote = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.revert.promote.001",
            "process_id": "process.formalization_promote_networked",
            "inputs": {"formalization_id": formalization_id, "allow_network_override": True},
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(promote.get("result", "")) != "complete":
        return {"status": "fail", "message": "promote failed in revert fixture"}
    graph_ref = str(promote.get("network_graph_ref", "")).strip()
    if not graph_ref:
        return {"status": "fail", "message": "promote fixture missing network graph ref"}

    revert = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.revert.raw.001",
            "process_id": "process.formalization_revert",
            "inputs": {"formalization_id": formalization_id, "remove_network_graph": True},
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(revert.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization_revert refused unexpectedly"}

    row = _state_row(state, formalization_id)
    if str(row.get("state", "")).strip() != "raw":
        return {"status": "fail", "message": "revert did not return formalization state to raw"}
    if _state_row(state, formalization_id).get("raw_sources") != sorted(set(raw_sources)):
        return {"status": "fail", "message": "revert did not preserve raw_sources"}
    if row.get("formal_artifact_ref") not in (None, "") or row.get("network_graph_ref") not in (None, ""):
        return {"status": "fail", "message": "revert did not clear formal/network refs"}
    if any(str(item.get("graph_id", "")).strip() == graph_ref for item in list(state.get("network_graphs") or []) if isinstance(item, dict)):
        return {"status": "fail", "message": "revert did not remove promoted network graph"}
    return {"status": "pass", "message": "revert restored raw lifecycle state and preserved raw_sources"}
