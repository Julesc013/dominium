"""FAST test: EMB-0 movement updates body position deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_movement_updates_position_deterministic"
TEST_TAGS = ["fast", "embodiment", "movement", "determinism"]


def _find_body(state: dict) -> dict:
    for row in list(state.get("body_assemblies") or []):
        if isinstance(row, dict) and str(row.get("assembly_id", "")) == "body.emb.test":
            return dict(row)
    return {}


def _find_body_state(state: dict) -> dict:
    for row in list(state.get("body_states") or []):
        if isinstance(row, dict) and str(row.get("subject_id", "")) == "agent.emb.test":
            return dict(row)
    return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.emb0_testlib import replay_body_motion

    first = replay_body_motion(gravity_vector=None, include_lens_update=False)
    second = replay_body_motion(gravity_vector=None, include_lens_update=False)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "EMB-0 movement replay must complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "EMB-0 movement final state hash diverged across replay"}

    final_state = dict(first.get("universe_state") or {})
    body_row = _find_body(final_state)
    body_state_row = _find_body_state(final_state)
    if not body_row or not body_state_row:
        return {"status": "fail", "message": "EMB-0 movement final state missing body or body_state rows"}
    transform = dict(body_row.get("transform_mm") or {})
    position_ref = dict(body_state_row.get("position_ref") or {})
    if int(transform.get("x", 0) or 0) <= 0:
        return {"status": "fail", "message": "EMB-0 movement did not advance body position"}
    if dict(transform) != dict(position_ref):
        return {"status": "fail", "message": "body_state position_ref must track authoritative body transform"}
    return {"status": "pass", "message": "EMB-0 movement determinism check passed"}
