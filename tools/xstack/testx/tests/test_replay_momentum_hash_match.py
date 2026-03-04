"""STRICT test: momentum/impulse hash chains are replay-stable across equivalent runs."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_replay_momentum_hash_match"
TEST_TAGS = ["strict", "physics", "momentum", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


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
    law = law_profile(["process.apply_impulse"])
    authority = authority_context()
    policy = policy_context()
    policy["physics_profile_id"] = "phys.realistic.default"

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.patch_a2.replay_momentum.001",
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.patch_a2.replay.001",
                "target_assembly_id": "body.vehicle.mob.free.alpha",
                "impulse_vector": {"x": 700, "y": -120, "z": 0},
                "torque_impulse": 2,
                "external_impulse_logged": False,
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
    if str(first_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first momentum replay fixture failed: {}".format(first_result)}
    if str(second_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second momentum replay fixture failed: {}".format(second_result)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    momentum_hash_a = str(first_state.get("momentum_hash_chain", "")).strip().lower()
    momentum_hash_b = str(second_state.get("momentum_hash_chain", "")).strip().lower()
    impulse_hash_a = str(first_state.get("impulse_event_hash_chain", "")).strip().lower()
    impulse_hash_b = str(second_state.get("impulse_event_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(momentum_hash_a)) or (not _HASH64.fullmatch(momentum_hash_b)):
        return {"status": "fail", "message": "momentum_hash_chain missing/invalid"}
    if (not _HASH64.fullmatch(impulse_hash_a)) or (not _HASH64.fullmatch(impulse_hash_b)):
        return {"status": "fail", "message": "impulse_event_hash_chain missing/invalid"}
    if momentum_hash_a != momentum_hash_b:
        return {"status": "fail", "message": "momentum_hash_chain drifted across equivalent runs"}
    if impulse_hash_a != impulse_hash_b:
        return {"status": "fail", "message": "impulse_event_hash_chain drifted across equivalent runs"}

    if list(first_state.get("momentum_states") or []) != list(second_state.get("momentum_states") or []):
        return {"status": "fail", "message": "momentum states drifted across equivalent runs"}
    if list(first_state.get("impulse_application_rows") or []) != list(second_state.get("impulse_application_rows") or []):
        return {"status": "fail", "message": "impulse rows drifted across equivalent runs"}
    return {"status": "pass", "message": "momentum replay hash chains are deterministic"}
