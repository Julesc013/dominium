"""STRICT test: precision quantization envelope stays stable across refinement."""

from __future__ import annotations

import sys


TEST_ID = "testx.epistemics.lod_precision_quantization_stable"
TEST_TAGS = ["strict", "epistemics", "lod", "observation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.lod_invariance_testlib import (
        base_state,
        execute_region_transition,
        observe_state,
    )

    state = base_state(camera_x_mm=12345)
    before = observe_state(state=state, memory_enabled=False)
    if str(before.get("result", "")) != "complete":
        return {"status": "fail", "message": "pre-refinement observation refused unexpectedly"}
    before_camera = dict((dict(before.get("perceived_model") or {}).get("camera_viewpoint") or {}))
    before_meta = dict((dict(before.get("perceived_model") or {}).get("metadata") or {}))

    expanded = execute_region_transition(
        state=state,
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
        desired_tier="fine",
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "region_expand refused unexpectedly during quantization stability check"}

    after = observe_state(state=state, memory_enabled=False)
    if str(after.get("result", "")) != "complete":
        return {"status": "fail", "message": "post-refinement observation refused unexpectedly"}
    after_camera = dict((dict(after.get("perceived_model") or {}).get("camera_viewpoint") or {}))
    after_meta = dict((dict(after.get("perceived_model") or {}).get("metadata") or {}))

    for key in ("position_mm", "orientation_mdeg"):
        if dict(before_camera.get(key) or {}) != dict(after_camera.get(key) or {}):
            return {"status": "fail", "message": "camera {} quantization changed after refinement".format(key)}
    if str(before_meta.get("lod_precision_envelope_id", "")) != str(after_meta.get("lod_precision_envelope_id", "")):
        return {"status": "fail", "message": "lod_precision_envelope_id changed after refinement"}
    return {"status": "pass", "message": "precision quantization stability across refinement passed"}

