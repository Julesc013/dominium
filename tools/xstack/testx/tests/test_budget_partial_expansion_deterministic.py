"""STRICT test: budget-capped partial cohort expansion is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.budget_partial_expansion_deterministic"
TEST_TAGS = ["strict", "civilisation", "cohort", "budget", "determinism"]


def _run_once():
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import (
        authority_context,
        base_state,
        law_profile,
        navigation_indices_for_roi,
        policy_context_for_roi,
    )

    state = copy.deepcopy(base_state())
    state["cohort_assemblies"] = [
        {
            "cohort_id": "cohort.budget.001",
            "size": 10,
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
    law = law_profile(["process.region_management_tick"])
    authority = authority_context(["session.boot"], privilege_level="observer")
    nav = navigation_indices_for_roi()
    policy = policy_context_for_roi(max_entities_micro=4, mapping_max_micro=10)

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.cohort.budget.tick.001",
            "process_id": "process.region_management_tick",
            "inputs": {},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices=nav,
        policy_context=policy,
    )
    if str(result.get("result", "")) != "complete":
        return result
    rows = [dict(item) for item in list(result.get("cohort_refinement") or []) if isinstance(item, dict)]
    if not rows:
        return {"result": "refused", "message": "no cohort_refinement rows emitted"}
    return {
        "result": "complete",
        "row": dict(rows[0]),
        "state_hash_anchor": str(result.get("state_hash_anchor", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "budget partial expansion run refused unexpectedly"}

    row_a = dict(first.get("row") or {})
    row_b = dict(second.get("row") or {})
    if row_a != row_b:
        return {"status": "fail", "message": "budget partial expansion decision row diverged across runs"}
    if str(first.get("state_hash_anchor", "")) != str(second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "budget partial expansion anchor diverged across runs"}

    if not bool(row_a.get("partial", False)):
        return {"status": "fail", "message": "expected partial expansion when budget caps micro agent count"}
    if int(row_a.get("target_micro_agents", 0) or 0) != 4:
        return {"status": "fail", "message": "target_micro_agents should match deterministic budget cap"}
    if int(row_a.get("expanded_micro_count", 0) or 0) != 4:
        return {"status": "fail", "message": "expanded_micro_count should equal deterministic budget cap"}
    return {"status": "pass", "message": "budget partial expansion determinism passed"}

