"""STRICT test: cross-shard cohort refinement refusal is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.cross_shard_cohort_refusal"
TEST_TAGS = ["strict", "civilisation", "cohort", "srz", "determinism"]


def _run_once():
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import authority_context, base_state, law_profile, mapping_policy_registry

    state = copy.deepcopy(base_state())
    state["cohort_assemblies"] = [
        {
            "cohort_id": "cohort.shard.001",
            "size": 5,
            "faction_id": None,
            "territory_id": None,
            "location_ref": "region.earth",
            "demographic_tags": {},
            "skill_distribution": {},
            "refinement_state": "macro",
            "created_tick": 0,
            "extensions": {"mapping_policy_id": "cohort.map.default"},
        }
    ]

    shard_map = {
        "object_owner": {
            "region.earth": "shard.0",
        },
        "shards": [
            {
                "shard_id": "shard.0",
                "region_scope": {"object_ids": ["region.earth"]},
            },
            {
                "shard_id": "shard.1",
                "region_scope": {"object_ids": ["region.mars"]},
            },
        ],
    }
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.cohort.expand.cross_shard.001",
            "process_id": "process.cohort_expand_to_micro",
            "inputs": {
                "cohort_id": "cohort.shard.001",
                "interest_region_id": "region.earth",
                "max_micro_agents": 3,
            },
        },
        law_profile=law_profile(["process.cohort_expand_to_micro"]),
        authority_context=authority_context(["entitlement.civ.admin"]),
        navigation_indices={},
        policy_context={
            "cohort_mapping_policy_registry": mapping_policy_registry(max_micro_agents_per_cohort=8),
            "pack_lock_hash": "d" * 64,
            "active_shard_id": "shard.1",
            "shard_map": shard_map,
        },
    )
    return {
        "result": result,
        "agent_states": list(state.get("agent_states") or []),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()

    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "refused" or str(second_result.get("result", "")) != "refused":
        return {"status": "fail", "message": "cross-shard cohort expansion must refuse deterministically"}

    first_refusal = dict(first_result.get("refusal") or {})
    second_refusal = dict(second_result.get("refusal") or {})
    if str(first_refusal.get("reason_code", "")) != "refusal.civ.cohort_cross_shard_forbidden":
        return {"status": "fail", "message": "expected refusal.civ.cohort_cross_shard_forbidden for cross-shard cohort expansion"}
    if first_refusal != second_refusal:
        return {"status": "fail", "message": "cross-shard cohort refusal payload must be deterministic"}

    if list(first.get("agent_states") or []) or list(second.get("agent_states") or []):
        return {"status": "fail", "message": "cross-shard cohort refusal must not create micro agent rows"}
    return {"status": "pass", "message": "cross-shard cohort expansion refusal determinism passed"}

