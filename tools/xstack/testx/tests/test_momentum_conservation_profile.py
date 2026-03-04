"""FAST test: momentum conservation profile logs untracked external impulses as exceptions."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_momentum_conservation_profile"
TEST_TAGS = ["fast", "physics", "conservation", "momentum"]


def _run_case(repo_root: str, *, external_logged: bool) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=0)
    law = law_profile(["process.apply_impulse"])
    authority = authority_context()
    policy = policy_context()
    policy["physics_profile_id"] = "phys.realistic.rank_strict"
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.momentum.profile.{}".format("logged" if external_logged else "unlogged"),
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.profile.{}".format("logged" if external_logged else "unlogged"),
                "target_assembly_id": "body.vehicle.mob.free.alpha",
                "impulse_vector": {"x": 120, "y": 0, "z": 0},
                "torque_impulse": 0,
                "external_impulse_logged": bool(external_logged),
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"state": state, "result": result}


def run(repo_root: str):
    logged = _run_case(repo_root=repo_root, external_logged=True)
    unlogged = _run_case(repo_root=repo_root, external_logged=False)
    logged_result = dict(logged.get("result") or {})
    unlogged_result = dict(unlogged.get("result") or {})
    if str(logged_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "logged impulse case refused: {}".format(logged_result)}
    if str(unlogged_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "unlogged impulse case refused: {}".format(unlogged_result)}

    logged_state = dict(logged.get("state") or {})
    if not list(logged_state.get("momentum_external_impulse_rows") or []):
        return {"status": "fail", "message": "strict momentum profile should record logged external impulses"}
    if list(logged_state.get("exception_events") or []):
        return {"status": "fail", "message": "logged external impulse should not raise conservation exception"}

    unlogged_state = dict(unlogged.get("state") or {})
    exception_rows = [dict(row) for row in list(unlogged_state.get("exception_events") or []) if isinstance(row, dict)]
    if not exception_rows:
        return {"status": "fail", "message": "unlogged external impulse must raise conservation exception_event"}
    reason_codes = sorted(set(str(row.get("reason_code", "")).strip() for row in exception_rows))
    if "physics.momentum.unlogged_external_impulse" not in reason_codes:
        return {"status": "fail", "message": "missing momentum conservation reason_code in exception events"}
    record_rows = [
        dict(row)
        for row in list(unlogged_state.get("info_artifact_rows") or [])
        if isinstance(row, dict) and str(row.get("artifact_family_id", "")).strip() == "RECORD"
    ]
    if not any(str((dict(row.get("extensions") or {})).get("artifact_type_id", "")).strip() == "artifact.exception_event" for row in record_rows):
        return {"status": "fail", "message": "exception_event must be projected as INFO family RECORD artifact"}
    return {"status": "pass", "message": "momentum conservation profile enforces exception logging for untracked impulses"}

