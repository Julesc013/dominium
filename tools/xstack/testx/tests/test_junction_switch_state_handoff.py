"""FAST test: blocked micro edge transition hands off using deterministic switch state."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.junction_switch_state_handoff"
TEST_TAGS = ["fast", "mobility", "micro", "junction", "switch"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_switch_handoff_state,
    )

    state = seed_switch_handoff_state()
    law = law_profile(["process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.micro.switch.handoff.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {
                        "throttle_permille": 0,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 16,
                        "max_brake_mm_per_tick2": 24,
                    }
                },
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )

    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "micro switch handoff fixture failed"}

    micro_row = next(
        (
            dict(row)
            for row in list(state.get("micro_motion_states") or [])
            if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.alpha"
        ),
        {},
    )
    if not micro_row:
        return {"status": "fail", "message": "missing micro state after switch handoff tick"}
    if str(micro_row.get("geometry_id", "")).strip() != "geometry.mob.micro.branch":
        return {"status": "fail", "message": "vehicle did not handoff to active switch outgoing geometry"}
    if int(micro_row.get("s_param", 0) or 0) != 0:
        return {"status": "fail", "message": "handoff should restart deterministic s_param at branch entry"}

    blocked_events = []
    for row in list(state.get("travel_events") or []):
        if not isinstance(row, dict):
            continue
        details = dict(row.get("details") or {})
        if str(details.get("reason_code", "")).strip() == "event.blocked":
            blocked_events.append(row)
    if blocked_events:
        return {"status": "fail", "message": "switch handoff should not emit event.blocked when branch exists"}

    return {"status": "pass", "message": "junction switch state handoff deterministic"}
