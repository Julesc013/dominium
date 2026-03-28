"""FAST test: MOB-9 wear state lowers derail threshold in micro constrained motion."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.wear.influences_derail_threshold"
TEST_TAGS = ["fast", "mobility", "wear", "micro", "derailment"]


def _run_case(*, high_wear: bool) -> dict:
    from mobility.maintenance import build_wear_state
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_micro_state,
    )

    state = seed_micro_state(
        min_curvature_radius_mm=2000,
        initial_s_param=1000,
        initial_velocity=300,
    )
    if high_wear:
        state["mobility_wear_states"] = [
            build_wear_state(
                target_id="edge.mob.micro.main",
                wear_type_id="wear.track",
                accumulated_value=200000,
                last_update_tick=0,
                extensions={},
            )
        ]
    else:
        state["mobility_wear_states"] = []
    law = law_profile(["process.mobility_micro_tick"])
    authority = authority_context()
    policy = policy_context()

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.wear.derail.threshold.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha"],
                "base_derail_threshold_units": 64,
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
    return {"result": result, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    low = _run_case(high_wear=False)
    high = _run_case(high_wear=True)
    low_result = dict(low.get("result") or {})
    high_result = dict(high.get("result") or {})
    if str(low_result.get("result", "")) != "complete" or str(high_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "micro tick fixture failed for wear threshold comparison"}

    low_derailed = set(str(item).strip() for item in list(low_result.get("derailed_vehicle_ids") or []) if str(item).strip())
    high_derailed = set(str(item).strip() for item in list(high_result.get("derailed_vehicle_ids") or []) if str(item).strip())
    if "vehicle.mob.micro.alpha" in low_derailed:
        return {"status": "fail", "message": "low-wear baseline unexpectedly derailed"}
    if "vehicle.mob.micro.alpha" not in high_derailed:
        return {"status": "fail", "message": "high-wear case did not lower threshold enough to derail"}
    return {"status": "pass", "message": "wear state influences derail threshold deterministically"}

