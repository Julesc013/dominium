"""STRICT test: FORM-1 promote_networked creates deterministic graph nodes/edges."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.infrastructure.formalization.promote_network_creates_graph_nodes"
TEST_TAGS = ["strict", "infrastructure", "formalization", "network"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(
        [
            "process.formalization_infer",
            "process.formalization_accept_candidate",
            "process.formalization_promote_networked",
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
    policy = policy_context()

    infer = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.promote.infer.001",
            "process_id": "process.formalization_infer",
            "inputs": {
                "formalization_id": "formalization.promote.alpha",
                "target_kind": "track",
                "target_context_id": "assembly.structure_instance.alpha",
                "raw_sources": ["part.a", "part.b", "part.c"],
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.inspect"], privilege_level="observer"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(infer.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization_infer failed in promote fixture"}
    candidates = [dict(item) for item in list(infer.get("candidates") or []) if isinstance(item, dict)]
    candidate_id = str((dict(candidates[0]) if candidates else {}).get("candidate_id", "")).strip()
    if not candidate_id:
        return {"status": "fail", "message": "missing candidate_id for promote fixture"}

    accept = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.promote.accept.001",
            "process_id": "process.formalization_accept_candidate",
            "inputs": {
                "formalization_id": "formalization.promote.alpha",
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
        return {"status": "fail", "message": "formalization_accept_candidate failed in promote fixture"}

    promote = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.promote.network.001",
            "process_id": "process.formalization_promote_networked",
            "inputs": {
                "formalization_id": "formalization.promote.alpha",
                "allow_network_override": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(promote.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization_promote_networked refused unexpectedly"}
    graph_id = str(promote.get("network_graph_ref", "")).strip()
    if not graph_id:
        return {"status": "fail", "message": "promote_networked missing network_graph_ref"}

    graph_rows = [dict(item) for item in list(state.get("network_graphs") or []) if isinstance(item, dict)]
    graph_row = {}
    for row in graph_rows:
        if str(row.get("graph_id", "")).strip() == graph_id:
            graph_row = dict(row)
            break
    if not graph_row:
        return {"status": "fail", "message": "promote_networked did not persist graph row"}
    if len(list(graph_row.get("nodes") or [])) < 2 or len(list(graph_row.get("edges") or [])) < 1:
        return {"status": "fail", "message": "promote_networked graph row missing deterministic nodes/edges"}
    return {"status": "pass", "message": "promote_networked created deterministic graph nodes/edges"}

