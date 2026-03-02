"""FAST test: micro free-motion tick remains deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.free_motion_deterministic"
TEST_TAGS = ["fast", "mobility", "micro", "free", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=8)
    law = law_profile(["process.mobility_free_tick"])
    authority = authority_context()
    policy = policy_context()
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.free.det.001",
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {
                        "throttle_permille": 700,
                        "brake_permille": 0,
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
        return {"status": "fail", "message": "free-motion deterministic fixture failed"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    for key in ("free_motion_states", "vehicle_motion_states", "body_assemblies", "travel_events"):
        if list(first_state.get(key) or []) != list(second_state.get(key) or []):
            return {"status": "fail", "message": "free-motion output drifted for '{}'".format(key)}

    runtime_row = dict(first_state.get("mobility_free_runtime_state") or {})
    if str(runtime_row.get("budget_outcome", "")).strip() != "complete":
        return {"status": "fail", "message": "expected complete budget_outcome for single-subject free-motion tick"}
    return {"status": "pass", "message": "free-motion deterministic tick verified"}

