"""FAST test: corridor clamp behavior is deterministic for free-motion subjects."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.corridor_clamp_deterministic"
TEST_TAGS = ["fast", "mobility", "micro", "free", "corridor"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(
        initial_velocity_x=30,
        corridor_geometry_id="geometry.mob.free.corridor.001",
    )
    # Move close to boundary to force deterministic clamp.
    for row in list(state.get("body_assemblies") or []):
        if str(row.get("assembly_id", "")).strip() == "body.vehicle.mob.free.alpha":
            row["transform_mm"] = {"x": 490, "y": 220, "z": 0}
            row["velocity_mm_per_tick"] = {"x": 30, "y": 30, "z": 0}
    law = law_profile(["process.mobility_free_tick"])
    authority = authority_context()
    policy = policy_context()

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.free.corridor.clamp.001",
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {"throttle_permille": 900, "strafe_permille": 900}
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
        return {"status": "fail", "message": "corridor clamp fixture failed"}

    first_bodies = {
        str(row.get("assembly_id", "")).strip(): dict(row)
        for row in list((dict(first.get("state") or {})).get("body_assemblies") or [])
        if isinstance(row, dict)
    }
    second_bodies = {
        str(row.get("assembly_id", "")).strip(): dict(row)
        for row in list((dict(second.get("state") or {})).get("body_assemblies") or [])
        if isinstance(row, dict)
    }
    alpha_a = dict(first_bodies.get("body.vehicle.mob.free.alpha") or {})
    alpha_b = dict(second_bodies.get("body.vehicle.mob.free.alpha") or {})
    if alpha_a != alpha_b:
        return {"status": "fail", "message": "clamped body transform drifted between equivalent runs"}

    pos = dict(alpha_a.get("transform_mm") or {})
    if int(pos.get("x", 0)) > 500 or int(pos.get("x", 0)) < 0:
        return {"status": "fail", "message": "corridor clamp did not enforce x boundary"}
    if int(pos.get("y", 0)) > 200 or int(pos.get("y", 0)) < -200:
        return {"status": "fail", "message": "corridor clamp did not enforce y boundary"}
    return {"status": "pass", "message": "corridor clamp deterministic and bounded"}

