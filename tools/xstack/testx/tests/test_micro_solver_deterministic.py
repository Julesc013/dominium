"""FAST test: micro constrained solver tick is deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.micro_solver_deterministic"
TEST_TAGS = ["fast", "mobility", "micro", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_micro_state,
    )

    state = seed_micro_state(initial_velocity=12)
    law = law_profile(["process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.micro.tick.det.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {
                        "throttle_permille": 700,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 40,
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
        return {"status": "fail", "message": "micro tick fixture failed"}

    first_micro = list((dict(first.get("state") or {})).get("micro_motion_states") or [])
    second_micro = list((dict(second.get("state") or {})).get("micro_motion_states") or [])
    if not first_micro or not second_micro:
        return {"status": "fail", "message": "missing micro motion rows after micro tick"}
    if first_micro != second_micro:
        return {"status": "fail", "message": "micro motion rows drifted across equivalent runs"}

    first_motion = list((dict(first.get("state") or {})).get("vehicle_motion_states") or [])
    second_motion = list((dict(second.get("state") or {})).get("vehicle_motion_states") or [])
    if first_motion != second_motion:
        return {"status": "fail", "message": "vehicle motion state rows drifted across equivalent runs"}

    alpha_row = next(
        (
            dict(row)
            for row in first_micro
            if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.alpha"
        ),
        {},
    )
    if int(alpha_row.get("s_param", 0) or 0) <= 0:
        return {"status": "fail", "message": "micro tick did not advance s_param for alpha vehicle"}

    return {"status": "pass", "message": "micro constrained solver deterministic"}
