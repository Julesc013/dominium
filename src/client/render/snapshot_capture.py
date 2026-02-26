"""Render snapshot capture pipeline over RenderModel artifacts."""

from __future__ import annotations

import json
import os
from typing import Dict

from .renderers.null_renderer import render_null_snapshot
from .renderers.software_renderer import render_software_snapshot


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _load_json(path: str) -> tuple[dict, str]:
    abs_path = os.path.normpath(os.path.abspath(path))
    if not os.path.isfile(abs_path):
        return {}, "missing file: {}".format(abs_path.replace("\\", "/"))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json: {}".format(abs_path.replace("\\", "/"))
    if not isinstance(payload, dict):
        return {}, "json root must be object: {}".format(abs_path.replace("\\", "/"))
    return payload, ""


def load_render_model_from_artifact(path: str) -> tuple[dict, str]:
    payload, err = _load_json(path)
    if err:
        return {}, err
    if "render_model" in payload and isinstance(payload.get("render_model"), dict):
        return dict(payload.get("render_model") or {}), ""
    if "renderables" in payload and "render_model_hash" in payload:
        return dict(payload), ""
    return {}, "input missing render_model payload: {}".format(os.path.normpath(os.path.abspath(path)).replace("\\", "/"))


def capture_render_snapshot(
    *,
    renderer_id: str,
    render_model: dict,
    out_dir: str,
    width: int = 0,
    height: int = 0,
    wireframe: bool = False,
) -> Dict[str, object]:
    renderer = str(renderer_id or "").strip().lower() or "null"
    if renderer == "null":
        return render_null_snapshot(
            render_model=dict(render_model or {}),
            out_dir=str(out_dir),
            renderer_id="null",
            image_width=max(0, _to_int(width, 0)),
            image_height=max(0, _to_int(height, 0)),
        )
    if renderer == "software":
        return render_software_snapshot(
            render_model=dict(render_model or {}),
            out_dir=str(out_dir),
            image_width=max(0, _to_int(width, 640)),
            image_height=max(0, _to_int(height, 360)),
            wireframe=bool(wireframe),
        )
    return {
        "result": "refusal",
        "code": "refusal.render.renderer_not_supported",
        "message": "renderer '{}' is not yet supported by capture pipeline".format(renderer),
    }
