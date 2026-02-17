"""STRICT test: RenderModel ordering/hash is deterministic for identical PerceivedModel input."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.render.render_model_deterministic_ordering"
TEST_TAGS = ["strict", "session", "render", "representation"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.render_order",
        "lens_id": "lens.diegetic.sensor",
        "camera_viewpoint": {
            "assembly_id": "camera.main",
            "frame_id": "frame.world",
            "view_mode_id": "view.third_person.player",
            "position_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        },
        "time_state": {"tick": 7, "rate_permille": 1000, "paused": False},
        "entities": {
            "entries": [
                {"entity_id": "agent.zeta", "transform_mm": {"x": 2, "y": 1, "z": 0}, "representation": {"shape_type": "aabb"}},
                {"entity_id": "agent.alpha", "transform_mm": {"x": 1, "y": 0, "z": 0}, "representation": {"shape_type": "capsule"}},
                {"entity_id": "agent.beta", "transform_mm": {"x": 3, "y": 0, "z": 0}, "representation": {"shape_type": "aabb"}},
            ]
        },
        "observed_entities": ["agent.zeta", "agent.alpha", "agent.beta"],
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.render_model import build_render_model

    first = build_render_model(copy.deepcopy(_perceived_model()), registry_payloads={})
    second = build_render_model(copy.deepcopy(_perceived_model()), registry_payloads={})
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "render build failed for deterministic ordering test"}
    if str(first.get("render_model_hash", "")) != str(second.get("render_model_hash", "")):
        return {"status": "fail", "message": "render model hash drifted across identical runs"}

    rows = list((dict(first.get("render_model") or {})).get("renderables") or [])
    semantic_ids = [str(dict(row).get("semantic_id", "")) for row in rows if isinstance(row, dict)]
    if semantic_ids != sorted(semantic_ids):
        return {"status": "fail", "message": "renderables are not sorted deterministically by semantic_id"}
    return {"status": "pass", "message": "render model ordering/hash deterministic"}
