"""FAST test: free-motion budget cap deterministically downgrades deferred subjects and logs decisions."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.free.budget_downgrade_logged"
TEST_TAGS = ["fast", "mobility", "micro", "free", "budget", "degrade"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(include_second_subject=True)
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.free.budget.degrade.001",
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha", "vehicle.mob.free.beta"],
                "roi_subject_ids": ["vehicle.mob.free.alpha", "vehicle.mob.free.beta"],
                "max_subject_updates_per_tick": 1,
                "downgrade_to_meso": True,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {"throttle_permille": 700},
                    "vehicle.mob.free.beta": {"throttle_permille": 700},
                },
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.mobility_free_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )

    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "free-motion budget fixture failed"}
    if str(ticked.get("budget_outcome", "")).strip() != "degraded":
        return {"status": "fail", "message": "expected degraded budget_outcome for capped free-motion updates"}
    deferred_ids = [str(item).strip() for item in list(ticked.get("deferred_subject_ids") or []) if str(item).strip()]
    if deferred_ids != ["vehicle.mob.free.beta"]:
        return {"status": "fail", "message": "deferred subject ordering should be deterministic by subject_id"}

    motion_rows = {
        str(row.get("vehicle_id", "")).strip(): dict(row)
        for row in list(state.get("vehicle_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip()
    }
    beta_motion = dict(motion_rows.get("vehicle.mob.free.beta") or {})
    if str(beta_motion.get("tier", "")).strip() != "meso":
        return {"status": "fail", "message": "deferred vehicle was not downgraded to meso tier"}

    decision_rows = [dict(row) for row in list(state.get("fidelity_decision_entries") or []) if isinstance(row, dict)]
    matching = [
        row
        for row in decision_rows
        if str(row.get("downgrade_reason", "")).strip() == "degrade.mob.free_budget"
        and str((dict(row.get("extensions") or {})).get("geometry_id", "")).strip() == "vehicle.mob.free.beta"
    ]
    if not matching:
        return {"status": "fail", "message": "free-motion budget downgrade decision log missing"}
    return {"status": "pass", "message": "free-motion budget downgrade logged deterministically"}

