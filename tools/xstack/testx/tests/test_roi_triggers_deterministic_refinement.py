"""STRICT test: ROI-driven cohort refinement is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.roi_triggers_deterministic_refinement"
TEST_TAGS = ["strict", "civilisation", "cohort", "roi", "determinism"]


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
            "cohort_id": "cohort.roi.001",
            "size": 6,
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
    policy = policy_context_for_roi(max_entities_micro=3, mapping_max_micro=6)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.cohort.roi.tick.001",
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
    return {
        "result": "complete",
        "state_hash_anchor": str(result.get("state_hash_anchor", "")),
        "cohort_refinement": list(result.get("cohort_refinement") or []),
        "universe_state": state,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "region_management_tick refused during cohort ROI determinism test"}

    refinement_a = list(first.get("cohort_refinement") or [])
    refinement_b = list(second.get("cohort_refinement") or [])
    if not refinement_a:
        return {"status": "fail", "message": "ROI tick did not emit cohort_refinement decisions"}
    if refinement_a != refinement_b:
        return {"status": "fail", "message": "ROI cohort refinement decisions diverged across repeated runs"}
    if str(first.get("state_hash_anchor", "")) != str(second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "ROI cohort refinement state hash anchor diverged across repeated runs"}

    action_tokens = sorted(str(row.get("action", "")) for row in refinement_a if isinstance(row, dict))
    if "expand" not in action_tokens:
        return {"status": "fail", "message": "ROI tick did not perform deterministic cohort expansion action"}
    return {"status": "pass", "message": "ROI-triggered cohort refinement determinism passed"}

