"""STRICT test: forced LOD information gain is refused in strict contract mode."""

from __future__ import annotations

import sys


TEST_ID = "testx.epistemics.lod_strict_mode_violation_refusal"
TEST_TAGS = ["strict", "epistemics", "lod", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.lod_invariance_testlib import base_state, execute_region_transition

    state = base_state(camera_x_mm=12345)
    refused = execute_region_transition(
        state=state,
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
        desired_tier="fine",
        force_information_gain=True,
    )
    if str(refused.get("result", "")) != "refused":
        return {"status": "fail", "message": "strict LOD violation path must refuse when forced leak hook is active"}
    refusal_payload = dict(refused.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.ep.lod_information_gain":
        return {"status": "fail", "message": "expected refusal.ep.lod_information_gain from strict LOD violation hook"}
    return {"status": "pass", "message": "strict LOD information gain refusal path passed"}

