"""FAST test: mobility wear accumulation is deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.wear.accumulation_deterministic"
TEST_TAGS = ["fast", "mobility", "wear", "maintenance", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_wear_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    state = seed_state()
    law = law_profile(["process.mobility_wear_tick"])
    authority = authority_context()
    policy = policy_context()

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.wear.tick.det.001",
            "process_id": "process.mobility_wear_tick",
            "inputs": {
                "include_auto_updates": False,
                "max_wear_updates_per_tick": 16,
                "wear_updates": [
                    {
                        "target_id": "edge.mob.travel.ab",
                        "wear_type_id": "wear.track",
                        "increment": 150,
                        "cycles": 1,
                        "dt_ticks": 1,
                    },
                    {
                        "target_id": "vehicle.mob.travel.alpha",
                        "wear_type_id": "wear.wheel",
                        "increment": 75,
                        "cycles": 1,
                        "dt_ticks": 1,
                    },
                    {
                        "target_id": "vehicle.mob.travel.alpha",
                        "wear_type_id": "wear.engine",
                        "increment": 50,
                        "cycles": 1,
                        "dt_ticks": 1,
                    },
                ],
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

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.mobility_wear_tick refused in deterministic fixture"}

    first_rows = [dict(row) for row in list((dict(first.get("state") or {})).get("mobility_wear_states") or []) if isinstance(row, dict)]
    second_rows = [dict(row) for row in list((dict(second.get("state") or {})).get("mobility_wear_states") or []) if isinstance(row, dict)]
    if first_rows != second_rows:
        return {"status": "fail", "message": "mobility_wear_states drifted across equivalent runs"}

    if int(first_result.get("processed_update_count", 0)) != 3:
        return {"status": "fail", "message": "expected 3 processed wear updates"}
    if int(first_result.get("threshold_crossing_count", 0)) != 0:
        return {"status": "fail", "message": "unexpected threshold crossing in deterministic wear fixture"}
    return {"status": "pass", "message": "mobility wear accumulation deterministic"}

