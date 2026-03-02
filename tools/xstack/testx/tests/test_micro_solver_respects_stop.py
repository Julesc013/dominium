"""FAST test: micro constrained solver obeys STOP signal aspects."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.micro_solver_respects_stop"
TEST_TAGS = ["fast", "mobility", "micro", "signal", "safety"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_signal_testlib import authority_context, law_profile, policy_context, seed_signal_state

    state = seed_signal_state(signal_count=1, initial_aspect="stop", initial_velocity=12)
    law = law_profile(["process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    before_row = next(
        (
            dict(row)
            for row in list(state.get("micro_motion_states") or [])
            if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.alpha"
        ),
        {},
    )
    before_s = int(before_row.get("s_param", 0) or 0)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.signal.micro.stop.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {
                        "throttle_permille": 900,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 50,
                    }
                },
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "micro tick refused in STOP-signal fixture"}

    after_row = next(
        (
            dict(row)
            for row in list(state.get("micro_motion_states") or [])
            if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.alpha"
        ),
        {},
    )
    if not after_row:
        return {"status": "fail", "message": "missing micro row after STOP signal tick"}
    if int(after_row.get("velocity", 0) or 0) != 0:
        return {"status": "fail", "message": "STOP signal should force velocity to zero"}
    if int(after_row.get("s_param", 0) or 0) != int(before_s):
        return {"status": "fail", "message": "STOP signal should prevent longitudinal advance along guide geometry"}
    return {"status": "pass", "message": "micro solver respects STOP signal aspect"}

