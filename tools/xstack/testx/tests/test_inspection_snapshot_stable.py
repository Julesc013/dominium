"""FAST test: MOB-9 inspection snapshot payload is stable for equivalent state."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.wear.inspection_snapshot_stable"
TEST_TAGS = ["fast", "mobility", "wear", "inspection", "determinism"]


def _run_once() -> dict:
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
            target_id="edge.mob.travel.ab",
            wear_type_id="wear.track",
            accumulated_value=4200,
            last_update_tick=0,
            extensions={},
        )
    ]
    law = law_profile(["process.inspect_track"])
    authority = authority_context()
    policy = policy_context()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.wear.inspect.track.001",
            "process_id": "process.inspect_track",
            "inputs": {"edge_id": "edge.mob.travel.ab"},
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
        return {"status": "fail", "message": "process.inspect_track refused in stability fixture"}

    first_rows = [dict(row) for row in list((dict(first.get("state") or {})).get("mobility_inspection_snapshots") or []) if isinstance(row, dict)]
    second_rows = [dict(row) for row in list((dict(second.get("state") or {})).get("mobility_inspection_snapshots") or []) if isinstance(row, dict)]
    if first_rows != second_rows:
        return {"status": "fail", "message": "inspection snapshot rows drifted across equivalent runs"}
    if not first_rows:
        return {"status": "fail", "message": "inspection snapshot rows missing"}
    if not str(first_rows[0].get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "inspection snapshot missing deterministic fingerprint"}
    return {"status": "pass", "message": "inspection snapshot stable for equivalent wear state"}

