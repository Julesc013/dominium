"""STRICT test: cohort expand/collapse conserves deterministic population counts."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.cohort_expand_collapse_conservation"
TEST_TAGS = ["strict", "civilisation", "cohort", "determinism"]


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script
    from tools.xstack.testx.tests.cohort_testlib import authority_context, base_state, law_profile, mapping_policy_registry

    intents = [
        {
            "intent_id": "intent.civ.cohort.create.001",
            "process_id": "process.cohort_create",
            "inputs": {
                "cohort_id": "cohort.test.001",
                "size": 7,
                "faction_id": None,
                "territory_id": None,
                "location_ref": "region.earth",
                "mapping_policy_id": "cohort.map.default",
            },
        },
        {
            "intent_id": "intent.civ.cohort.expand.001",
            "process_id": "process.cohort_expand_to_micro",
            "inputs": {
                "cohort_id": "cohort.test.001",
                "interest_region_id": "region.earth",
                "max_micro_agents": 4,
            },
        },
        {
            "intent_id": "intent.civ.cohort.collapse.001",
            "process_id": "process.cohort_collapse_from_micro",
            "inputs": {
                "cohort_id": "cohort.test.001",
            },
        },
    ]
    return replay_intent_script(
        universe_state=copy.deepcopy(base_state()),
        law_profile=law_profile(
            [
                "process.cohort_create",
                "process.cohort_expand_to_micro",
                "process.cohort_collapse_from_micro",
            ]
        ),
        authority_context=authority_context(["entitlement.civ.admin"]),
        intents=intents,
        navigation_indices={},
        policy_context={
            "cohort_mapping_policy_registry": mapping_policy_registry(max_micro_agents_per_cohort=8),
            "pack_lock_hash": "a" * 64,
        },
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "cohort expand/collapse replay must complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "cohort expand/collapse final hash diverged across runs"}

    state = dict(first.get("universe_state") or {})
    cohort_rows = sorted(
        (dict(row) for row in list(state.get("cohort_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("cohort_id", "")),
    )
    if len(cohort_rows) != 1:
        return {"status": "fail", "message": "expected one cohort row after create/expand/collapse"}
    cohort_row = cohort_rows[0]
    if str(cohort_row.get("cohort_id", "")) != "cohort.test.001":
        return {"status": "fail", "message": "unexpected cohort id after replay"}
    if int(cohort_row.get("size", 0) or 0) != 7:
        return {"status": "fail", "message": "cohort size was not conserved across expand/collapse"}
    if str(cohort_row.get("refinement_state", "")) != "macro":
        return {"status": "fail", "message": "cohort must return to macro refinement state after collapse"}
    remaining_micro = [
        dict(row)
        for row in list(state.get("agent_states") or [])
        if isinstance(row, dict) and str(row.get("parent_cohort_id", "")).strip() == "cohort.test.001"
    ]
    if remaining_micro:
        return {"status": "fail", "message": "collapse left micro cohort agents in agent_states"}
    return {"status": "pass", "message": "cohort expand/collapse conservation passed"}

