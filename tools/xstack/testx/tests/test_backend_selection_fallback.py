"""STRICT test: hardware backend requests fall back deterministically when unavailable."""

from __future__ import annotations

import copy
import os
import shutil
import sys
import tempfile


TEST_ID = "testx.render.backend_selection_fallback"
TEST_TAGS = ["strict", "render", "backend"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.backend_fallback",
        "camera_viewpoint": {
            "view_mode_id": "view.third_person.player",
            "position_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        },
        "time_state": {"tick": 9},
        "entities": {
            "entries": [
                {
                    "entity_id": "agent.alpha",
                    "representation": {"shape_type": "capsule"},
                    "transform_mm": {"x": 0, "y": 0, "z": 1800},
                }
            ]
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.render.snapshot_capture import capture_render_snapshot
    from tools.xstack.sessionx.render_model import build_render_model

    render_model = dict(build_render_model(copy.deepcopy(_perceived_model()), registry_payloads={}).get("render_model") or {})
    temp_root = tempfile.mkdtemp(prefix="testx_renderer_fallback_")
    try:
        result = capture_render_snapshot(
            renderer_id="hardware_gl",
            render_model=render_model,
            out_dir=temp_root,
            cache_dir=temp_root,
            width=256,
            height=144,
            backend_policy={"disabled_backends": ["hardware_gl"]},
        )
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "capture did not complete for fallback path"}
        if str(result.get("effective_renderer_id", "")) != "software":
            return {
                "status": "fail",
                "message": "fallback effective renderer mismatch: {}".format(result.get("effective_renderer_id")),
            }
        fallback = dict(result.get("fallback_event") or {})
        if str(fallback.get("reason_code", "")) != "refusal.render.backend_unavailable":
            return {"status": "fail", "message": "missing deterministic fallback reason code"}
        event_path = str(result.get("fallback_event_path", "")).strip()
        if not event_path or not os.path.isfile(event_path):
            return {"status": "fail", "message": "fallback run-meta event artifact missing"}
        return {"status": "pass", "message": "backend selection fallback deterministically downgraded to software"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
