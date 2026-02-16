"""STRICT test: RenderModel adapter falls back deterministically to pill proxy when assets are missing."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.representation.render_proxy_fallback"
TEST_TAGS = ["strict", "session", "representation", "render"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.render_fallback",
        "lens_id": "lens.diegetic.sensor",
        "camera_viewpoint": {
            "assembly_id": "camera.main",
            "frame_id": "frame.world",
            "position_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        },
        "time_state": {"tick": 0, "rate_permille": 1000, "paused": False},
        "entities": {
            "entries": [
                {
                    "entity_id": "agent.alpha",
                    "transform_mm": {"x": 10, "y": 20, "z": 30},
                    "representation": {
                        "shape_type": "capsule",
                        "cosmetic_id": "cosmetic.humanoid.highdetail.default",
                        "render_proxy_id": "render.proxy.humanoid_highdetail",
                        "mesh_ref": "",
                        "material_ref": "",
                    },
                }
            ]
        },
        "observed_entities": ["agent.alpha"],
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.render_model import build_render_model

    render = build_render_model(copy.deepcopy(_perceived_model()))
    if str(render.get("result", "")) != "complete":
        return {"status": "fail", "message": "render model build failed for deterministic fallback test"}
    render_model = dict(render.get("render_model") or {})
    rows = sorted(
        (dict(row) for row in list(render_model.get("renderables") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("renderable_id", "")),
    )
    if len(rows) != 1:
        return {"status": "fail", "message": "expected single renderable for fallback test"}
    row = rows[0]
    if str(row.get("render_proxy_id", "")) != "render.proxy.pill_default":
        return {"status": "fail", "message": "missing-asset renderable did not fallback to pill proxy id"}
    if str(row.get("mesh_ref", "")) != "asset.mesh.pill.default":
        return {"status": "fail", "message": "missing-asset renderable did not fallback to pill mesh"}
    if str(row.get("material_ref", "")) != "asset.material.pill.default":
        return {"status": "fail", "message": "missing-asset renderable did not fallback to pill material"}
    return {"status": "pass", "message": "render proxy fallback path is deterministic"}

