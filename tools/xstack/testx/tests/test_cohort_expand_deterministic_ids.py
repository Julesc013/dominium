"""STRICT test: cohort expansion emits deterministic micro agent IDs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.cohort_expand_deterministic_ids"
TEST_TAGS = ["strict", "civilisation", "cohort", "determinism"]


def _run_once():
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import authority_context, base_state, law_profile, mapping_policy_registry

    state = copy.deepcopy(base_state())
    law = law_profile(["process.cohort_create", "process.cohort_expand_to_micro"])
    authority = authority_context(["entitlement.civ.admin"])
    policy = {
        "cohort_mapping_policy_registry": mapping_policy_registry(max_micro_agents_per_cohort=6),
        "pack_lock_hash": "b" * 64,
    }

    create = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.cohort.create.ids",
            "process_id": "process.cohort_create",
            "inputs": {
                "cohort_id": "cohort.test.ids",
                "size": 6,
                "location_ref": "region.earth",
                "mapping_policy_id": "cohort.map.default",
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(create.get("result", "")) != "complete":
        return create

    expand = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.cohort.expand.ids",
            "process_id": "process.cohort_expand_to_micro",
            "inputs": {
                "cohort_id": "cohort.test.ids",
                "interest_region_id": "region.earth",
                "max_micro_agents": 6,
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(expand.get("result", "")) != "complete":
        return expand
    return {
        "result": "complete",
        "state_hash_anchor": str(expand.get("state_hash_anchor", "")),
        "created_agent_ids": list(expand.get("created_agent_ids") or []),
        "universe_state": state,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "cohort create/expand execution refused unexpectedly"}

    ids_a = list(first.get("created_agent_ids") or [])
    ids_b = list(second.get("created_agent_ids") or [])
    if not ids_a:
        return {"status": "fail", "message": "cohort expansion did not create deterministic micro IDs"}
    if ids_a != ids_b:
        return {"status": "fail", "message": "cohort expansion micro IDs diverged across repeated runs"}
    if ids_a != sorted(ids_a):
        return {"status": "fail", "message": "cohort expansion micro IDs are not deterministically sorted"}
    if any(not str(token).startswith("agent.") for token in ids_a):
        return {"status": "fail", "message": "cohort expansion produced malformed micro agent id prefix"}
    if str(first.get("state_hash_anchor", "")) != str(second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "cohort expansion anchor diverged across repeated runs"}
    return {"status": "pass", "message": "cohort deterministic micro ID generation passed"}

