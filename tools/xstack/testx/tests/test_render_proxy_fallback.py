"""STRICT test: RenderModel adapter degrades deterministically without external assets."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.representation.no_assets_required"
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

    render = build_render_model(copy.deepcopy(_perceived_model()), registry_payloads={})
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
    if str(row.get("primitive_id", "")) != "prim.capsule.default":
        return {"status": "fail", "message": "missing-asset renderable did not resolve to deterministic capsule primitive"}
    material_id = str(row.get("material_id", "")).strip()
    if not material_id:
        return {"status": "fail", "message": "renderable missing procedural material_id"}
    extension_materials = list((dict(render_model.get("extensions") or {})).get("materials") or [])
    material_rows = [dict(item) for item in extension_materials if isinstance(item, dict)]
    if not any(str(item.get("material_id", "")) == material_id for item in material_rows):
        return {"status": "fail", "message": "procedural material payload is missing for resolved renderable"}
    return {"status": "pass", "message": "render model no-assets fallback is deterministic"}
