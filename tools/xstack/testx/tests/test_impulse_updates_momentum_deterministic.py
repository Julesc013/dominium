"""FAST test: process.apply_impulse deterministically updates momentum state."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_impulse_updates_momentum_deterministic"
TEST_TAGS = ["fast", "physics", "momentum", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _momentum_row(state: dict, assembly_id: str) -> dict:
    token = str(assembly_id or "").strip()
    for row in list(state.get("momentum_states") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == token:
            return dict(row)
    return {}


def _run_once(repo_root: str) -> dict:
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
    body_id = "body.vehicle.mob.free.alpha"
    law = law_profile(["process.apply_impulse"])
    authority = authority_context()
    policy = policy_context()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.impulse.det.001",
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.test.alpha.0001",
                "target_assembly_id": body_id,
                "impulse_vector": {"x": 900, "y": -300, "z": 0},
                "torque_impulse": 4,
                "external_impulse_logged": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": dict(result), "state": dict(state)}


def run(repo_root: str):
    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "first apply_impulse run refused: {}".format(first_result)}
    if str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "second apply_impulse run refused: {}".format(second_result)}

    body_id = "body.vehicle.mob.free.alpha"
    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    row_a = _momentum_row(first_state, body_id)
    row_b = _momentum_row(second_state, body_id)
    if (not row_a) or (not row_b):
        return {"status": "fail", "message": "apply_impulse did not persist momentum state row"}
    expected_linear = {"x": 900, "y": -300, "z": 0}
    if dict(row_a.get("momentum_linear") or {}) != expected_linear:
        return {"status": "fail", "message": "unexpected momentum_linear delta after impulse"}
    if int(row_a.get("momentum_angular", 0) or 0) != 4:
        return {"status": "fail", "message": "unexpected momentum_angular delta after impulse"}
    if dict(row_a) != dict(row_b):
        return {"status": "fail", "message": "momentum state drifted across deterministic runs"}

    if len(list(first_state.get("impulse_application_rows") or [])) != 1:
        return {"status": "fail", "message": "expected one impulse_application row"}
    if list(first_state.get("impulse_application_rows") or []) != list(second_state.get("impulse_application_rows") or []):
        return {"status": "fail", "message": "impulse application rows are not deterministic"}
    first_chain = str(first_state.get("momentum_hash_chain", "")).strip().lower()
    second_chain = str(second_state.get("momentum_hash_chain", "")).strip().lower()
    if not _HASH64.fullmatch(first_chain):
        return {"status": "fail", "message": "momentum_hash_chain missing after impulse"}
    if first_chain != second_chain:
        return {"status": "fail", "message": "momentum_hash_chain drifted across deterministic runs"}
    first_impulse_chain = str(first_state.get("impulse_event_hash_chain", "")).strip().lower()
    second_impulse_chain = str(second_state.get("impulse_event_hash_chain", "")).strip().lower()
    if not _HASH64.fullmatch(first_impulse_chain):
        return {"status": "fail", "message": "impulse_event_hash_chain missing after impulse"}
    if first_impulse_chain != second_impulse_chain:
        return {"status": "fail", "message": "impulse_event_hash_chain drifted across deterministic runs"}
    return {"status": "pass", "message": "impulse process updates momentum deterministically"}

