"""STRICT test: null renderer summary hash must be deterministic."""

from __future__ import annotations

import copy
import shutil
import sys
import tempfile


TEST_ID = "testx.render.null_renderer_summary_deterministic"
TEST_TAGS = ["strict", "render", "renderer"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.null_renderer",
        "camera_viewpoint": {"view_mode_id": "view.third_person.player"},
        "time_state": {"tick": 9},
        "entities": {
            "entries": [
                {"entity_id": "agent.alpha", "representation": {"shape_type": "capsule"}, "transform_mm": {"x": 100, "y": 0, "z": 1000}},
                {"entity_id": "agent.beta", "representation": {"shape_type": "aabb"}, "transform_mm": {"x": 200, "y": 50, "z": 1200}},
            ]
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from client.render.snapshot_capture import capture_render_snapshot
    from tools.xstack.sessionx.render_model import build_render_model

    render_model = dict(build_render_model(copy.deepcopy(_perceived_model()), registry_payloads={}).get("render_model") or {})
    temp_root = tempfile.mkdtemp(prefix="testx_null_renderer_")
    try:
        first = capture_render_snapshot(
            renderer_id="null",
            render_model=render_model,
            out_dir=temp_root,
            cache_dir=temp_root,
            width=0,
            height=0,
        )
        second = capture_render_snapshot(
            renderer_id="null",
            render_model=render_model,
            out_dir=temp_root,
            cache_dir=temp_root,
            width=0,
            height=0,
        )
        if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
            return {"status": "fail", "message": "null renderer capture did not complete"}
        if str(first.get("summary_hash", "")) != str(second.get("summary_hash", "")):
            return {"status": "fail", "message": "null renderer summary hash drifted"}
        return {"status": "pass", "message": "null renderer summary hash is deterministic"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
