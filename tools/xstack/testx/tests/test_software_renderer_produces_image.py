"""STRICT test: software renderer produces image artifact and stable summary hash."""

from __future__ import annotations

import copy
import os
import shutil
import sys
import tempfile


TEST_ID = "testx.render.software_renderer_produces_image"
TEST_TAGS = ["strict", "render", "renderer"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.software_renderer",
        "camera_viewpoint": {
            "view_mode_id": "view.third_person.player",
            "position_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        },
        "time_state": {"tick": 15},
        "entities": {
            "entries": [
                {"entity_id": "agent.alpha", "representation": {"shape_type": "capsule"}, "transform_mm": {"x": 0, "y": 0, "z": 1800}},
                {"entity_id": "agent.beta", "representation": {"shape_type": "aabb"}, "transform_mm": {"x": 400, "y": 0, "z": 2000}},
            ]
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.client.render.snapshot_capture import capture_render_snapshot
    from tools.xstack.sessionx.render_model import build_render_model

    render_model = dict(build_render_model(copy.deepcopy(_perceived_model()), registry_payloads={}).get("render_model") or {})
    temp_root = tempfile.mkdtemp(prefix="testx_software_renderer_")
    try:
        first = capture_render_snapshot(
            renderer_id="software",
            render_model=render_model,
            out_dir=temp_root,
            cache_dir=temp_root,
            width=256,
            height=144,
            wireframe=True,
        )
        second = capture_render_snapshot(
            renderer_id="software",
            render_model=render_model,
            out_dir=temp_root,
            cache_dir=temp_root,
            width=256,
            height=144,
            wireframe=True,
        )
        if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
            return {"status": "fail", "message": "software renderer capture did not complete"}
        image_path = str(first.get("image_path", "")).strip()
        if not image_path or not os.path.isfile(image_path):
            return {"status": "fail", "message": "software renderer image artifact missing"}
        if str(first.get("summary_hash", "")) != str(second.get("summary_hash", "")):
            return {"status": "fail", "message": "software renderer summary hash drifted"}
        return {"status": "pass", "message": "software renderer produced image and stable summary hash"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
