"""FAST test: ROI free-motion derives velocity from momentum state."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_velocity_derived_from_momentum"
TEST_TAGS = ["fast", "physics", "mobility", "momentum"]


def _body_row(state: dict, assembly_id: str) -> dict:
    token = str(assembly_id or "").strip()
    for row in list(state.get("body_assemblies") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == token:
            return dict(row)
    return {}


def _momentum_row(state: dict, assembly_id: str) -> dict:
    token = str(assembly_id or "").strip()
    for row in list(state.get("momentum_states") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == token:
            return dict(row)
    return {}


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.physics import build_momentum_state
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=0)
    body_id = "body.vehicle.mob.free.alpha"
    state["momentum_states"] = [
        build_momentum_state(
            assembly_id=body_id,
            mass_value=5,
            momentum_linear={"x": 150, "y": 0, "z": 0},
            momentum_angular=0,
            last_update_tick=0,
            extensions={},
        )
    ]
    law = law_profile(["process.mobility_free_tick"])
    authority = authority_context()
    policy = policy_context()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.mobility.momentum.001",
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {
                        "throttle_permille": 0,
                        "brake_permille": 0,
                        "move_vector_permille": {"x": 0, "y": 0, "z": 0},
                    }
                },
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": dict(result), "state": dict(state)}


def run(repo_root: str):
    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "first mobility_free_tick run refused: {}".format(first_result)}
    if str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "second mobility_free_tick run refused: {}".format(second_result)}

    body_id = "body.vehicle.mob.free.alpha"
    expected_velocity_x = 30  # momentum(150) / mass(5)
    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    body_a = _body_row(first_state, body_id)
    body_b = _body_row(second_state, body_id)
    if (not body_a) or (not body_b):
        return {"status": "fail", "message": "expected body row missing after mobility_free_tick"}
    vel_a = int((dict(body_a.get("velocity_mm_per_tick") or {})).get("x", 0) or 0)
    pos_a = int((dict(body_a.get("transform_mm") or {})).get("x", 0) or 0)
    if vel_a != expected_velocity_x:
        return {"status": "fail", "message": "velocity was not derived from momentum/mass"}
    if pos_a != expected_velocity_x:
        return {"status": "fail", "message": "position integration did not use momentum-derived velocity"}
    if dict(body_a) != dict(body_b):
        return {"status": "fail", "message": "mobility body state drifted across deterministic runs"}

    momentum_a = _momentum_row(first_state, body_id)
    if dict(momentum_a.get("momentum_linear") or {}) != {"x": 150, "y": 0, "z": 0}:
        return {"status": "fail", "message": "momentum state drifted after zero-control free-motion tick"}
    return {"status": "pass", "message": "ROI mobility derives velocity from momentum state"}

