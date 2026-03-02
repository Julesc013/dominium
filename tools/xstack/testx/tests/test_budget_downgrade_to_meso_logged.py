"""FAST test: micro solver budget cap deterministically downgrades deferred vehicles to meso and logs decisions."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.budget_downgrade_to_meso_logged"
TEST_TAGS = ["fast", "mobility", "micro", "budget", "degrade"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_micro_state,
    )

    state = seed_micro_state(initial_velocity=8, include_second_vehicle=True)
    law = law_profile(["process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.micro.budget.degrade.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha", "vehicle.mob.micro.beta"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha", "vehicle.mob.micro.beta"],
                "max_vehicle_updates_per_tick": 1,
                "downgrade_to_meso_on_budget": True,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {
                        "throttle_permille": 600,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 30,
                        "max_brake_mm_per_tick2": 24,
                    },
                    "vehicle.mob.micro.beta": {
                        "throttle_permille": 600,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 30,
                        "max_brake_mm_per_tick2": 24,
                    },
                },
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )

    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "budget downgrade fixture failed"}
    if str(ticked.get("budget_outcome", "")).strip() != "degraded":
        return {"status": "fail", "message": "expected degraded budget_outcome for capped micro updates"}

    deferred_ids = [str(item).strip() for item in list(ticked.get("deferred_vehicle_ids") or []) if str(item).strip()]
    if deferred_ids != ["vehicle.mob.micro.beta"]:
        return {"status": "fail", "message": "deferred vehicle ordering should be deterministic by vehicle_id"}

    motion_rows = {
        str(row.get("vehicle_id", "")).strip(): dict(row)
        for row in list(state.get("vehicle_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip()
    }
    beta_motion = dict(motion_rows.get("vehicle.mob.micro.beta") or {})
    if str(beta_motion.get("tier", "")).strip() != "meso":
        return {"status": "fail", "message": "deferred vehicle was not deterministically downgraded to meso tier"}

    decision_rows = [dict(row) for row in list(state.get("fidelity_decision_entries") or []) if isinstance(row, dict)]
    matching = [
        row
        for row in decision_rows
        if str(row.get("downgrade_reason", "")).strip() == "degrade.mob.micro_budget"
        and str((dict(row.get("extensions") or {})).get("geometry_id", "")).strip() == "vehicle.mob.micro.beta"
    ]
    if not matching:
        return {"status": "fail", "message": "budget downgrade decision log entry missing for deferred vehicle"}

    return {"status": "pass", "message": "budget downgrade to meso logged deterministically"}
