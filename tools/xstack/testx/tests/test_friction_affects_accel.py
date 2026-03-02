"""FAST test: lower friction deterministically reduces free-motion acceleration outcome."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.friction_affects_accel"
TEST_TAGS = ["fast", "mobility", "micro", "free", "fields"]


def _tick_with_friction(repo_root: str, friction_permille: int) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(friction_permille=int(friction_permille))
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.free.friction.{}".format(int(friction_permille)),
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {"throttle_permille": 900, "brake_permille": 0}
                },
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.mobility_free_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    return {"result": ticked, "state": state}


def run(repo_root: str):
    high = _tick_with_friction(repo_root, 1000)
    low = _tick_with_friction(repo_root, 300)
    if str(dict(high.get("result") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "high-friction fixture failed"}
    if str(dict(low.get("result") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "low-friction fixture failed"}

    def _velocity_x(payload: dict) -> int:
        rows = [
            dict(row)
            for row in list(payload.get("free_motion_states") or [])
            if isinstance(row, dict) and str(row.get("subject_id", "")).strip() == "vehicle.mob.free.alpha"
        ]
        if not rows:
            return 0
        return int((dict(rows[0].get("velocity") or {})).get("x", 0) or 0)

    high_v = _velocity_x(dict(high.get("state") or {}))
    low_v = _velocity_x(dict(low.get("state") or {}))
    if not (high_v > low_v):
        return {
            "status": "fail",
            "message": "friction did not reduce velocity outcome deterministically (high={}, low={})".format(
                high_v,
                low_v,
            ),
        }
    return {"status": "pass", "message": "friction deterministically reduced acceleration/velocity outcome"}

