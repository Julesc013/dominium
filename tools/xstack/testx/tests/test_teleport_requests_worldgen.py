"""FAST test: UX-0 teleport plans enqueue deterministic refinement before camera moves when needed."""

from __future__ import annotations

import sys


TEST_ID = "test_teleport_requests_worldgen"
TEST_TAGS = ["fast", "ux", "viewer", "teleport", "worldgen"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.ui.teleport_controller import RNG_UI_TELEPORT_RANDOM_STAR, build_teleport_plan
    from tools.xstack.testx.tests.ux0_testlib import candidate_system_rows

    rows = candidate_system_rows(repo_root)
    if not rows:
        return {"status": "fail", "message": "UX-0 teleport fixture produced no candidate systems"}
    plan = build_teleport_plan(
        repo_root=repo_root,
        command="/tp random_star",
        universe_seed="42",
        authority_mode="dev",
        teleport_counter=3,
        candidate_system_rows=rows,
    )
    if str(plan.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "UX-0 teleport plan did not complete"}
    process_sequence = list(plan.get("process_sequence") or [])
    if len(process_sequence) < 2:
        return {"status": "fail", "message": "UX-0 teleport plan did not emit the expected process sequence"}
    if str(dict(process_sequence[0]).get("process_id", "")).strip() != "process.refinement_request_enqueue":
        return {"status": "fail", "message": "UX-0 teleport must enqueue refinement before camera teleport"}
    if str(dict(process_sequence[1]).get("process_id", "")).strip() != "process.camera_teleport":
        return {"status": "fail", "message": "UX-0 teleport plan did not emit camera teleport after worldgen"}
    if str(plan.get("rng_stream_id", "")).strip() != RNG_UI_TELEPORT_RANDOM_STAR:
        return {"status": "fail", "message": "UX-0 random_star teleport did not log its named RNG stream"}
    refinement_request = dict((dict(process_sequence[0]).get("inputs") or {}).get("refinement_request_record") or {})
    if str(dict(refinement_request).get("request_kind", "")).strip() != "teleport":
        return {"status": "fail", "message": "UX-0 teleport refinement request kind drifted"}
    return {"status": "pass", "message": "UX-0 teleport enqueues deterministic refinement before camera movement"}
