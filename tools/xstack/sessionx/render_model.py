"""Deterministic RenderModel adapter that accepts PerceivedModel input only."""

from __future__ import annotations

from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256


def _renderables(perceived_model: dict) -> List[dict]:
    out = []
    for entity_id in sorted(str(item).strip() for item in (perceived_model.get("observed_entities") or []) if str(item).strip()):
        out.append(
            {
                "renderable_id": "renderable.{}".format(entity_id),
                "entity_id": entity_id,
                "transform_ref": "transform.identity",
            }
        )
    return out


def build_render_model(perceived_model: dict) -> Dict[str, object]:
    """Build minimal presentation payload from PerceivedModel without TruthModel access."""
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
