"""FAST test: wind vector deterministically introduces free-motion drift."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.wind_drift_effect"
TEST_TAGS = ["fast", "mobility", "micro", "free", "fields"]


def _run_with_wind(repo_root: str, wind_y: int) -> dict:
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
        wind_vector={"x": 0, "y": int(wind_y), "z": 0},
    )
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.free.wind.{}".format(int(wind_y)),
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {"throttle_permille": 0, "brake_permille": 0}
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
    no_wind = _run_with_wind(repo_root, 0)
    with_wind = _run_with_wind(repo_root, 300)
    if str(dict(no_wind.get("result") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "no-wind fixture failed"}
    if str(dict(with_wind.get("result") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "wind fixture failed"}

    def _velocity_y(payload: dict) -> int:
        rows = [
            dict(row)
            for row in list(payload.get("free_motion_states") or [])
            if isinstance(row, dict) and str(row.get("subject_id", "")).strip() == "vehicle.mob.free.alpha"
        ]
        if not rows:
            return 0
        return int((dict(rows[0].get("velocity") or {})).get("y", 0) or 0)

    no_wind_vy = _velocity_y(dict(no_wind.get("state") or {}))
    wind_vy = _velocity_y(dict(with_wind.get("state") or {}))
    if abs(wind_vy) <= abs(no_wind_vy):
        return {
            "status": "fail",
            "message": "wind drift did not influence lateral velocity (no_wind={}, wind={})".format(
                no_wind_vy,
                wind_vy,
            ),
        }

    events = [dict(row) for row in list((dict(with_wind.get("state") or {})).get("travel_events") or []) if isinstance(row, dict)]
    if not any(str((dict(row.get("details") or {})).get("reason_code", "")).strip() == "incident.wind_exceeded" for row in events):
        return {"status": "fail", "message": "wind drift warning incident event missing"}
    return {"status": "pass", "message": "wind drift deterministically influences free-motion state"}

