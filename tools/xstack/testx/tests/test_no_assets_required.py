"""STRICT test: RenderModel adapter emits valid primitives/materials without asset packs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.render.no_assets_required"
TEST_TAGS = ["strict", "render", "representation"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.render_no_assets",
        "lens_id": "lens.diegetic.sensor",
        "camera_viewpoint": {
            "assembly_id": "camera.main",
            "frame_id": "frame.world",
            "view_mode_id": "view.third_person.player",
            "position_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        },
        "time_state": {"tick": 0, "rate_permille": 1000, "paused": False},
        "entities": {
            "entries": [
                {
                    "entity_id": "agent.alpha",
                    "entity_kind": "agent",
                    "transform_mm": {"x": 10, "y": 20, "z": 30},
                    "representation": {
                        "shape_type": "capsule",
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
        return {"status": "fail", "message": "render build failed with empty registry payloads"}

    render_model = dict(render.get("render_model") or {})
    renderables = [dict(row) for row in list(render_model.get("renderables") or []) if isinstance(row, dict)]
    if len(renderables) != 1:
        return {"status": "fail", "message": "expected one renderable in no-assets test"}
    row = renderables[0]
    if str(row.get("primitive_id", "")) != "prim.capsule.default":
        return {"status": "fail", "message": "no-assets path did not resolve deterministic primitive fallback"}
    material_id = str(row.get("material_id", "")).strip()
    if not material_id:
        return {"status": "fail", "message": "no-assets path missing procedural material_id"}

    extension_materials = list((dict(render_model.get("extensions") or {})).get("materials") or [])
    if not any(str(dict(item).get("material_id", "")) == material_id for item in extension_materials if isinstance(item, dict)):
        return {"status": "fail", "message": "no-assets path missing procedural material payload"}
    return {"status": "pass", "message": "render path remains valid with zero assets"}

