"""Deterministic RenderModel adapter that accepts PerceivedModel input only."""

from __future__ import annotations

from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_RENDER_PROXY_ID = "render.proxy.pill_default"
DEFAULT_MESH_REF = "asset.mesh.pill.default"
DEFAULT_MATERIAL_REF = "asset.material.pill.default"


def _proxy_label(render_proxy_id: str) -> str:
    token = str(render_proxy_id).strip()
    if token == "render.proxy.humanoid_highdetail":
        return "humanoid_highdetail"
    if token == "render.proxy.humanoid_lowpoly":
        return "humanoid_lowpoly"
    return "pill"


def _renderables(perceived_model: dict) -> List[dict]:
    out = []
    entities = dict(perceived_model.get("entities") or {})
    entries = list(entities.get("entries") or [])
    for row in sorted((dict(item) for item in entries if isinstance(item, dict)), key=lambda item: str(item.get("entity_id", ""))):
        entity_id = str(row.get("entity_id", "")).strip()
        if not entity_id:
            continue
        representation = dict(row.get("representation") or {})
        render_proxy_id = str(representation.get("render_proxy_id", "")).strip() or DEFAULT_RENDER_PROXY_ID
        mesh_ref = str(representation.get("mesh_ref", "")).strip()
        material_ref = str(representation.get("material_ref", "")).strip()
        if not mesh_ref or not material_ref:
            render_proxy_id = DEFAULT_RENDER_PROXY_ID
            mesh_ref = DEFAULT_MESH_REF
            material_ref = DEFAULT_MATERIAL_REF
        out.append(
            {
                "renderable_id": "renderable.{}".format(entity_id),
                "entity_id": entity_id,
                "render_proxy_id": render_proxy_id,
                "mesh_ref": mesh_ref,
                "material_ref": material_ref,
                "transform_mm": dict(row.get("transform_mm") or {"x": 0, "y": 0, "z": 0}),
                "text_proxy": "Agent[{}] ({})".format(entity_id, _proxy_label(render_proxy_id)),
            }
        )

    if out:
        return out

    for entity_id in sorted(str(item).strip() for item in (perceived_model.get("observed_entities") or []) if str(item).strip()):
        out.append(
            {
                "renderable_id": "renderable.{}".format(entity_id),
                "entity_id": entity_id,
                "render_proxy_id": DEFAULT_RENDER_PROXY_ID,
                "mesh_ref": DEFAULT_MESH_REF,
                "material_ref": DEFAULT_MATERIAL_REF,
                "transform_mm": {"x": 0, "y": 0, "z": 0},
                "text_proxy": "Agent[{}] (pill)".format(entity_id),
            }
        )
    return out


def build_render_model(perceived_model: dict) -> Dict[str, object]:
    """Build minimal presentation payload strictly from PerceivedModel input."""
    source_hash = canonical_sha256(perceived_model)
    camera_viewpoint = dict(perceived_model.get("camera_viewpoint") or {})
    time_state = dict(perceived_model.get("time_state") or {})
    render_model = {
        "schema_version": "1.0.0",
        "source_perceived_hash": source_hash,
        "viewpoint_id": str(perceived_model.get("viewpoint_id", "")),
        "lens_id": str(perceived_model.get("lens_id", "")),
        "camera_viewpoint": camera_viewpoint,
        "time_state": time_state,
        "renderables": _renderables(perceived_model),
    }
    return {
        "result": "complete",
        "render_model": render_model,
        "render_model_hash": canonical_sha256(render_model),
    }
