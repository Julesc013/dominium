"""STRICT test: FORM-1 inference process does not mutate network/truth substrates."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.infrastructure.formalization.inference_does_not_mutate_truth"
TEST_TAGS = ["strict", "infrastructure", "formalization", "process"]


def _law_profile():
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(["process.formalization_infer"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.formalization_infer"] = "entitlement.inspect"
    privileges["process.formalization_infer"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, base_state, policy_context

    state = base_state()
    state["network_graphs"] = []
    state["material_commitments"] = []
    state["construction_commitments"] = []
    state_before = copy.deepcopy(state)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.form.infer.truth.001",
            "process_id": "process.formalization_infer",
            "inputs": {
                "formalization_id": "formalization.truth.alpha",
                "target_kind": "track",
                "target_context_id": "assembly.structure_instance.alpha",
                "raw_sources": ["part.a", "part.b", "part.c"],
                "max_search_cost_units": 8,
            },
        },
        law_profile=_law_profile(),
        authority_context=authority_context(["entitlement.inspect"], privilege_level="observer"),
        navigation_indices={},
        policy_context=policy_context(),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "formalization_infer refused unexpectedly"}

    if list(state.get("network_graphs") or []):
        return {"status": "fail", "message": "inference process must not create network graph truth rows"}
    if list(state.get("material_commitments") or []) or list(state.get("construction_commitments") or []):
        return {"status": "fail", "message": "inference process must not create commitments"}

    for key in ("installed_structure_instances", "construction_projects", "construction_steps"):
        if list(state.get(key) or []) != list(state_before.get(key) or []):
            return {"status": "fail", "message": "inference process unexpectedly mutated '{}' truth rows".format(key)}
    if not list(state.get("formalization_inference_candidates") or []):
        return {"status": "fail", "message": "inference process did not emit derived inference candidates"}
    return {"status": "pass", "message": "inference process preserved truth/network substrates"}

