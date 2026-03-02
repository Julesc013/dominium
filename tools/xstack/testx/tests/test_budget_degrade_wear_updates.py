"""FAST test: wear update budget degradation is deterministic and logged."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.wear.budget_degrade_wear_updates"
TEST_TAGS = ["fast", "mobility", "wear", "budget", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_wear_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    state = seed_state()
    law = law_profile(["process.mobility_wear_tick"])
    authority = authority_context()
    policy = policy_context()
    updates = []
    for index in range(8):
        updates.append(
            {
                "target_id": "vehicle.mob.travel.alpha",
                "wear_type_id": "wear.engine",
                "increment": 10 + index,
                "cycles": 1,
                "dt_ticks": 1,
            }
        )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.wear.budget.001",
            "process_id": "process.mobility_wear_tick",
            "inputs": {
                "include_auto_updates": False,
                "max_wear_updates_per_tick": 2,
                "wear_updates": updates,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": result, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.mobility_wear_tick refused in budget fixture"}

    if str(first_result.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected degraded budget_outcome for constrained wear updates"}
    if int(first_result.get("pending_update_count", 0)) <= 0:
        return {"status": "fail", "message": "expected pending updates after wear budget degradation"}

    first_pending = list((dict(first.get("state") or {})).get("mobility_wear_pending_updates") or [])
    second_pending = list((dict(second.get("state") or {})).get("mobility_wear_pending_updates") or [])
    if first_pending != second_pending:
        return {"status": "fail", "message": "pending wear update ordering drifted across equivalent runs"}
    return {"status": "pass", "message": "wear budget degradation deterministic and stable"}

