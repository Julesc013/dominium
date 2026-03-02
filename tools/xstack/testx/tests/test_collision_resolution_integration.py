"""FAST test: free-motion updates pass through EB collision resolution deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.free.collision_resolution_integration"
TEST_TAGS = ["fast", "mobility", "micro", "free", "collision"]


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

    state = seed_free_state(
        initial_velocity_x=120,
        with_collision_obstacle=True,
    )
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.free.collision.001",
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {"throttle_permille": 1000, "brake_permille": 0}
                },
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.mobility_free_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "collision integration fixture failed"}

    collision_state = dict(state.get("collision_state") or {})
    if int(collision_state.get("last_tick_pair_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "collision subsystem did not register any candidate pair"}

    events = [dict(row) for row in list(state.get("travel_events") or []) if isinstance(row, dict)]
    if not any(str((dict(row.get("details") or {})).get("reason_code", "")).strip() == "incident.collision" for row in events):
        return {"status": "fail", "message": "collision incident event missing from travel event stream"}

    incidents = [dict(row) for row in list(state.get("mobility_free_incidents") or []) if isinstance(row, dict)]
    if not any(str(row.get("kind", "")).strip() == "collision" for row in incidents):
        return {"status": "fail", "message": "collision incident missing from mobility_free_incidents"}
    return {"status": "pass", "message": "collision integration verified for free-motion process path"}

