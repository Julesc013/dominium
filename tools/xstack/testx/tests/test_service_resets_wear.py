"""FAST test: service process reduces mobility wear deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.wear.service_resets_wear"
TEST_TAGS = ["fast", "mobility", "wear", "maintenance", "service"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.mobility.maintenance import build_wear_state
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_wear_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    state = seed_state()
    state["mobility_wear_states"] = [
        build_wear_state(
            target_id="vehicle.mob.travel.alpha",
            wear_type_id="wear.engine",
            accumulated_value=1200,
            last_update_tick=0,
            extensions={},
        ),
        build_wear_state(
            target_id="vehicle.mob.travel.alpha",
            wear_type_id="wear.brake",
            accumulated_value=800,
            last_update_tick=0,
            extensions={},
        ),
    ]
    law = law_profile(["process.service_vehicle"])
    authority = authority_context()
    policy = policy_context()

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.wear.service.vehicle.001",
            "process_id": "process.service_vehicle",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.alpha",
                "reset_fraction_numerator": 1,
                "reset_fraction_denominator": 1,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.service_vehicle refused in reset fixture"}

    rows = [
        dict(row)
        for row in list(state.get("mobility_wear_states") or [])
        if isinstance(row, dict) and str(row.get("target_id", "")).strip() == "vehicle.mob.travel.alpha"
    ]
    if not rows:
        return {"status": "fail", "message": "missing vehicle wear rows after service"}
    for row in rows:
        if int(row.get("accumulated_value", -1)) != 0:
            return {"status": "fail", "message": "service did not reset accumulated wear to zero"}
    serviced_rows = [dict(row) for row in list(result.get("serviced_rows") or []) if isinstance(row, dict)]
    if len(serviced_rows) < 2:
        return {"status": "fail", "message": "expected serviced_rows entries for engine and brake wear"}
    return {"status": "pass", "message": "service process reset mobility wear deterministically"}

