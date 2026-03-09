"""FAST test: EMB-0 body tick applies gravity through the PHYS field path."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_gravity_applies"
TEST_TAGS = ["fast", "embodiment", "physics", "gravity"]


def _find_row(rows: object, key: str, value: str) -> dict:
    token = str(value or "").strip()
    for row in list(rows or []):
        if not isinstance(row, dict):
            continue
        if str(row.get(key, "")).strip() == token:
            return dict(row)
    return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.emb0_testlib import authority_context, law_profile, policy_context, seed_embodied_state

    state = seed_embodied_state(gravity_vector={"x": 0, "y": -9, "z": 0}, mass_value=5)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.emb.body_tick.gravity.001",
            "process_id": "process.body_tick",
            "inputs": {
                "body_id": "body.emb.test",
                "dt_ticks": 1,
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.body_tick"])),
        authority_context=copy.deepcopy(authority_context([], privilege_level="observer")),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "body_tick refused gravity test: {}".format(result)}

    force_row = _find_row(state.get("force_application_rows"), "target_assembly_id", "body.emb.test")
    if not force_row:
        return {"status": "fail", "message": "gravity body_tick did not persist a force_application row"}
    expected_force = {"x": 0, "y": -720000, "z": 0}
    if dict(force_row.get("force_vector") or {}) != expected_force:
        return {"status": "fail", "message": "gravity force vector mismatch for EMB-0 body tick"}

    momentum_row = _find_row(state.get("momentum_states"), "assembly_id", "body.emb.test")
    if not momentum_row:
        return {"status": "fail", "message": "gravity body_tick did not update momentum state"}
    linear = dict(momentum_row.get("momentum_linear") or {})
    if int(linear.get("y", 0) or 0) >= 0:
        return {"status": "fail", "message": "gravity body_tick must drive negative Y momentum for the fixture"}
    return {"status": "pass", "message": "EMB-0 gravity coupling check passed"}
