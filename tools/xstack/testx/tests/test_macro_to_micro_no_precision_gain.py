"""STRICT test: macro->micro refinement must not leak additional precision."""

from __future__ import annotations

import sys


TEST_ID = "testx.epistemics.lod_macro_to_micro_no_precision_gain"
TEST_TAGS = ["strict", "epistemics", "lod", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.lod_invariance_testlib import base_state, execute_region_transition

    state = base_state(camera_x_mm=12345)
    result = execute_region_transition(
        state=state,
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
        desired_tier="fine",
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "region_expand refused unexpectedly during LOD precision gain check"}

    lod_summary = dict(result.get("lod_invariance") or {})
    if str(lod_summary.get("status", "")) != "ok":
        return {"status": "fail", "message": "region_expand LOD invariance did not return status=ok"}
    if bool(lod_summary.get("precision_gain", True)):
        return {"status": "fail", "message": "macro->micro refinement reported precision_gain=true"}
    if list(lod_summary.get("new_channels") or []):
        return {"status": "fail", "message": "macro->micro refinement exposed unexpected new channels"}
    if list(lod_summary.get("new_entities") or []):
        return {"status": "fail", "message": "macro->micro refinement exposed unexpected new entities"}
    if list(lod_summary.get("sensitive_paths") or []):
        return {"status": "fail", "message": "macro->micro refinement exposed sensitive internal-state paths"}
    return {"status": "pass", "message": "macro->micro no-precision-gain invariance check passed"}

