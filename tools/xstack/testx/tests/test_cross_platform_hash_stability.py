"""STRICT test: momentum/impulse hash chains stay stable across equivalent row ordering variants."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_cross_platform_hash_stability"
TEST_TAGS = ["strict", "physics", "determinism", "hash"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _momentum_row(state: dict, assembly_id: str) -> dict:
    token = str(assembly_id or "").strip()
    for row in list(state.get("momentum_states") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == token:
            return dict(row)
    return {}


def _run_variant(repo_root: str, *, reverse_order: bool) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.physics import build_impulse_application, build_momentum_state
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=0, include_second_subject=True)
    body_a = "body.vehicle.mob.free.alpha"
    body_b = "body.vehicle.mob.free.beta"

    momentum_rows = [
        build_momentum_state(
            assembly_id=body_a,
            mass_value=3,
            momentum_linear={"x": 90, "y": 0, "z": 0},
            momentum_angular=0,
            last_update_tick=0,
            extensions={},
        ),
        build_momentum_state(
            assembly_id=body_b,
            mass_value=2,
            momentum_linear={"x": -20, "y": 10, "z": 0},
            momentum_angular=1,
            last_update_tick=0,
            extensions={},
        ),
    ]
    prior_impulses = [
        build_impulse_application(
            application_id="impulse.history.aa",
            target_assembly_id=body_a,
            impulse_vector={"x": 5, "y": 0, "z": 0},
            torque_impulse=0,
            originating_process_id="process.apply_impulse",
            extensions={},
        ),
        build_impulse_application(
            application_id="impulse.history.bb",
            target_assembly_id=body_b,
            impulse_vector={"x": 0, "y": -2, "z": 0},
            torque_impulse=0,
            originating_process_id="process.apply_impulse",
            extensions={},
        ),
    ]
    if reverse_order:
        momentum_rows = list(reversed(momentum_rows))
        prior_impulses = list(reversed(prior_impulses))
    state["momentum_states"] = list(momentum_rows)
    state["impulse_application_rows"] = list(prior_impulses)

    law = law_profile(["process.apply_impulse"])
    authority = authority_context()
    policy = policy_context()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.hash.stability.{}".format("b" if reverse_order else "a"),
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.hash.stability",
                "target_assembly_id": body_a,
                "impulse_vector": {"x": 12, "y": -3, "z": 0},
                "torque_impulse": 2,
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
    first = _run_variant(repo_root=repo_root, reverse_order=False)
    second = _run_variant(repo_root=repo_root, reverse_order=True)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline hash variant refused: {}".format(first_result)}
    if str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "reordered hash variant refused: {}".format(second_result)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    momentum_chain_a = str(first_state.get("momentum_hash_chain", "")).strip().lower()
    momentum_chain_b = str(second_state.get("momentum_hash_chain", "")).strip().lower()
    impulse_chain_a = str(first_state.get("impulse_event_hash_chain", "")).strip().lower()
    impulse_chain_b = str(second_state.get("impulse_event_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(momentum_chain_a)) or (not _HASH64.fullmatch(momentum_chain_b)):
        return {"status": "fail", "message": "momentum_hash_chain missing for ordering variants"}
    if (not _HASH64.fullmatch(impulse_chain_a)) or (not _HASH64.fullmatch(impulse_chain_b)):
        return {"status": "fail", "message": "impulse_event_hash_chain missing for ordering variants"}
    if momentum_chain_a != momentum_chain_b:
        return {"status": "fail", "message": "momentum_hash_chain changed for equivalent ordering variants"}
    if impulse_chain_a != impulse_chain_b:
        return {"status": "fail", "message": "impulse_event_hash_chain changed for equivalent ordering variants"}

    body_a = "body.vehicle.mob.free.alpha"
    momentum_a = _momentum_row(first_state, body_a)
    momentum_b = _momentum_row(second_state, body_a)
    if dict(momentum_a) != dict(momentum_b):
        return {"status": "fail", "message": "momentum row drifted across equivalent ordering variants"}
    return {"status": "pass", "message": "momentum/impulse hash chains stable across ordering variants"}

