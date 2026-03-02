"""STRICT test: ROI entry/exit for free-motion is deterministic and collapse preserves anchor state."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.transition_roi_entry_exit_deterministic"
TEST_TAGS = ["strict", "mobility", "roi", "transition", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=12)
    law = law_profile(["process.mobility_free_tick"])
    authority = authority_context()
    policy = policy_context()

    entry_tick = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.transition.roi.entry.001",
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.alpha"],
                "dt_ticks": 1,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {"throttle_permille": 700, "brake_permille": 0}
                },
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(entry_tick.get("result", "")).strip() != "complete":
        return {"result": entry_tick, "state": state}
    entry_motion_rows = {
        str(row.get("vehicle_id", "")).strip(): dict(row)
        for row in list(state.get("vehicle_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip()
    }
    entry_anchor = dict((dict(entry_motion_rows.get("vehicle.mob.free.alpha") or {})).get("micro_state") or {})

    exit_tick = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.transition.roi.exit.001",
            "process_id": "process.mobility_free_tick",
            "inputs": {
                "subject_ids": ["vehicle.mob.free.alpha"],
                "roi_subject_ids": ["vehicle.mob.free.non_roi"],
                "dt_ticks": 1,
                "downgrade_to_meso": True,
                "control_inputs_by_subject": {
                    "vehicle.mob.free.alpha": {"throttle_permille": 700, "brake_permille": 0}
                },
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"entry": entry_tick, "exit": exit_tick, "state": state, "entry_anchor": entry_anchor}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_entry = dict(first.get("entry") or {})
    first_exit = dict(first.get("exit") or {})
    second_entry = dict(second.get("entry") or {})
    second_exit = dict(second.get("exit") or {})
    if str(first_entry.get("result", "")).strip() != "complete" or str(first_exit.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ROI entry/exit fixture failed on first run"}
    if str(second_entry.get("result", "")).strip() != "complete" or str(second_exit.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ROI entry/exit fixture failed on second run"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    if list(first_state.get("free_motion_states") or []) != list(second_state.get("free_motion_states") or []):
        return {"status": "fail", "message": "free-motion state drifted across equivalent ROI entry/exit runs"}
    if list(first_state.get("vehicle_motion_states") or []) != list(second_state.get("vehicle_motion_states") or []):
        return {"status": "fail", "message": "vehicle motion tiers drifted across equivalent ROI entry/exit runs"}
    if list(first_state.get("travel_events") or []) != list(second_state.get("travel_events") or []):
        return {"status": "fail", "message": "travel event stream drifted across equivalent ROI entry/exit runs"}

    deferred_ids = [str(item).strip() for item in list(first_exit.get("deferred_subject_ids") or []) if str(item).strip()]
    if deferred_ids != ["vehicle.mob.free.alpha"]:
        return {"status": "fail", "message": "ROI exit should deterministically defer/collapse non-ROI subject"}

    rows = {
        str(row.get("vehicle_id", "")).strip(): dict(row)
        for row in list(first_state.get("vehicle_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip()
    }
    alpha_row = dict(rows.get("vehicle.mob.free.alpha") or {})
    if str(alpha_row.get("tier", "")).strip() != "meso":
        return {"status": "fail", "message": "ROI exit did not collapse free-motion vehicle to meso"}

    entry_micro_anchor = dict(first.get("entry_anchor") or {})
    exit_micro_anchor = dict(alpha_row.get("micro_state") or {})
    if entry_micro_anchor != exit_micro_anchor:
        return {"status": "fail", "message": "ROI exit collapse changed micro anchor state unexpectedly"}
    return {"status": "pass", "message": "ROI entry/exit transition is deterministic and anchor-preserving"}
