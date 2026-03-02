"""FAST test: deterministic derailment threshold triggers process-managed derail transition."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.derailment_threshold_trigger"
TEST_TAGS = ["fast", "mobility", "micro", "derailment"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_micro_state,
    )

    state = seed_micro_state(
        min_curvature_radius_mm=200,
        initial_s_param=1000,
        initial_velocity=320,
    )
    law = law_profile(["process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.micro.derail.threshold.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha"],
                "base_derail_threshold_units": 32,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {
                        "throttle_permille": 0,
                        "brake_permille": 0,
                        "max_accel_mm_per_tick2": 16,
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

    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "micro tick refused in derailment threshold fixture"}

    derailed_ids = [str(item).strip() for item in list(ticked.get("derailed_vehicle_ids") or []) if str(item).strip()]
    if "vehicle.mob.micro.alpha" not in set(derailed_ids):
        return {"status": "fail", "message": "expected deterministic derailment did not trigger"}

    motion_rows = [
        dict(row)
        for row in list(state.get("vehicle_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.alpha"
    ]
    if not motion_rows:
        return {"status": "fail", "message": "missing vehicle motion state after derailment"}
    micro_state = dict(motion_rows[0].get("micro_state") or {})
    if not str(micro_state.get("body_ref", "")).strip():
        return {"status": "fail", "message": "derailment did not create free body_ref for collision handoff"}

    incident_rows = []
    for row in list(state.get("travel_events") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("kind", "")).strip() != "incident_stub":
            continue
        details = dict(row.get("details") or {})
        reason_code = str(details.get("reason_code", "")).strip()
        if reason_code.startswith("incident.derailment."):
            incident_rows.append(row)
    if not incident_rows:
        return {"status": "fail", "message": "derailment incident event was not logged"}

    return {"status": "pass", "message": "derailment threshold trigger and incident logging passed"}
