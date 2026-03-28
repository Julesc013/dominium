"""STRICT test: render snapshot and summary artifacts expose required schema fields."""

from __future__ import annotations

import copy
import os
import shutil
import sys
import tempfile


TEST_ID = "testx.render.render_snapshot_schema_valid"
TEST_TAGS = ["strict", "render", "schema"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.snapshot_schema",
        "camera_viewpoint": {"view_mode_id": "view.third_person.player"},
        "time_state": {"tick": 12},
        "entities": {"entries": [{"entity_id": "agent.alpha", "representation": {"shape_type": "capsule"}, "transform_mm": {"x": 0, "y": 0, "z": 900}}]},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from client.render.snapshot_capture import capture_render_snapshot
    from tools.xstack.sessionx.render_model import build_render_model

    render_model = dict(build_render_model(copy.deepcopy(_perceived_model()), registry_payloads={}).get("render_model") or {})
    temp_root = tempfile.mkdtemp(prefix="testx_render_snapshot_schema_")
    try:
        captured = capture_render_snapshot(
            renderer_id="null",
            render_model=render_model,
            out_dir=temp_root,
            cache_dir=temp_root,
            width=0,
            height=0,
        )
        if str(captured.get("result", "")) != "complete":
            return {"status": "fail", "message": "render snapshot capture failed"}
        snapshot = dict(captured.get("render_snapshot") or {})
        summary = dict(captured.get("frame_summary") or {})
        required_snapshot = (
            "snapshot_id",
            "tick",
            "viewpoint_id",
            "render_model_hash",
            "pack_lock_hash",
            "physics_profile_id",
            "renderer_id",
            "image_width",
            "image_height",
            "pixel_format",
            "summary_hash",
            "outputs",
        )
        for key in required_snapshot:
            if key not in snapshot:
                return {"status": "fail", "message": "snapshot missing required field '{}'".format(key)}
        outputs = dict(snapshot.get("outputs") or {})
        if not str(outputs.get("summary_ref", "")).strip():
            return {"status": "fail", "message": "snapshot.outputs.summary_ref is required"}

        required_summary = ("render_model_hash", "primitive_counts", "layer_counts", "label_count", "deterministic_fingerprint")
        for key in required_summary:
            if key not in summary:
                return {"status": "fail", "message": "frame summary missing required field '{}'".format(key)}

        summary_path = str(captured.get("summary_path", "")).strip()
        if not summary_path or not os.path.isfile(summary_path):
            return {"status": "fail", "message": "summary artifact path missing"}
        return {"status": "pass", "message": "render snapshot summary schema fields are present"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
