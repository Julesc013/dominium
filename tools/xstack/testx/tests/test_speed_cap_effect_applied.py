"""FAST test: speed-cap effects deterministically clamp micro constrained velocity."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.speed_cap_effect_applied"
TEST_TAGS = ["fast", "mobility", "micro", "effects"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        attach_speed_cap_effect,
        authority_context,
        law_profile,
        policy_context,
        seed_micro_state,
    )

    state = seed_micro_state(initial_velocity=0)
    state = attach_speed_cap_effect(state, vehicle_id="vehicle.mob.micro.alpha", max_speed_permille=200)
    law = law_profile(["process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.micro.speed_cap.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha"],
                "default_speed_cap_mm_per_tick": 1000,
                "dt_ticks": 1,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {
                        "throttle_permille": 1000,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 800,
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
    return {"result": ticked, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "speed cap fixture failed"}

    first_row = next(
        (
            dict(row)
            for row in list((dict(first.get("state") or {})).get("micro_motion_states") or [])
            if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.alpha"
        ),
        {},
    )
    second_row = next(
        (
            dict(row)
            for row in list((dict(second.get("state") or {})).get("micro_motion_states") or [])
            if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.alpha"
        ),
        {},
    )
    if not first_row or not second_row:
        return {"status": "fail", "message": "missing micro state row for speed cap assertion"}

    first_velocity = int(first_row.get("velocity", 0) or 0)
    second_velocity = int(second_row.get("velocity", 0) or 0)
    if first_velocity <= 0:
        return {"status": "fail", "message": "micro tick did not produce positive velocity under throttle"}
    if first_velocity > 200:
        return {"status": "fail", "message": "speed cap effect was not applied to micro velocity"}
    if first_velocity != second_velocity:
        return {"status": "fail", "message": "speed cap application drifted across equivalent runs"}

    return {"status": "pass", "message": "speed cap effect deterministically clamps micro velocity"}
