"""FAST test: coupling constraints deterministically enforce consist trailing offsets."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.coupling_consist_order_deterministic"
TEST_TAGS = ["fast", "mobility", "micro", "coupling", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_micro_state,
    )

    state = seed_micro_state(initial_velocity=0, include_second_vehicle=True)
    law = law_profile(["process.coupler_attach", "process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    attach = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.micro.coupler.attach.001",
            "process_id": "process.coupler_attach",
            "inputs": {
                "vehicle_a_id": "vehicle.mob.micro.alpha",
                "vehicle_b_id": "vehicle.mob.micro.beta",
                "coupling_type_id": "coupler.basic",
                "coupling_offset_mm": 10,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(attach.get("result", "")) != "complete":
        return {"result": attach, "state": state}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.micro.coupler.tick.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha", "vehicle.mob.micro.beta"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha", "vehicle.mob.micro.beta"],
                "dt_ticks": 1,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {
                        "throttle_permille": 800,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 40,
                        "max_brake_mm_per_tick2": 24,
                    },
                    "vehicle.mob.micro.beta": {
                        "throttle_permille": 0,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 40,
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
    return {"result": ticked, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "coupling fixture failed"}

    first_constraints = list((dict(first.get("state") or {})).get("coupling_constraints") or [])
    second_constraints = list((dict(second.get("state") or {})).get("coupling_constraints") or [])
    if not first_constraints or not second_constraints:
        return {"status": "fail", "message": "missing coupling constraints after coupler attach"}
    if first_constraints != second_constraints:
        return {"status": "fail", "message": "coupling constraints drifted across equivalent runs"}

    first_by_vehicle = {
        str(row.get("vehicle_id", "")).strip(): dict(row)
        for row in list((dict(first.get("state") or {})).get("micro_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip()
    }
    if "vehicle.mob.micro.alpha" not in first_by_vehicle or "vehicle.mob.micro.beta" not in first_by_vehicle:
        return {"status": "fail", "message": "missing micro motion rows for coupled vehicles"}
    lead_s = int((dict(first_by_vehicle["vehicle.mob.micro.alpha"]).get("s_param", 0) or 0))
    trail_s = int((dict(first_by_vehicle["vehicle.mob.micro.beta"]).get("s_param", 0) or 0))
    expected_trail = max(0, lead_s - 10)
    if trail_s != expected_trail:
        return {
            "status": "fail",
            "message": "coupled trailing s_param did not match deterministic lead offset propagation",
        }

    second_by_vehicle = {
        str(row.get("vehicle_id", "")).strip(): dict(row)
        for row in list((dict(second.get("state") or {})).get("micro_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip()
    }
    if first_by_vehicle != second_by_vehicle:
        return {"status": "fail", "message": "coupled micro rows drifted across equivalent runs"}

    return {"status": "pass", "message": "coupling consist order and offsets deterministic"}
