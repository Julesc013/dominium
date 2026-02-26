"""Deterministic null renderer producing derived snapshot artifacts."""

from __future__ import annotations

import json
import os
from typing import Dict, Iterable, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _sorted_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _primitive_type_from_id(primitive_id: str) -> str:
    token = str(primitive_id).strip().lower()
    if token.startswith("prim."):
        parts = token.split(".")
        if len(parts) >= 2 and parts[1]:
            return str(parts[1])
    return "unknown"


def _normalized_renderables(render_model: dict) -> List[dict]:
    rows = []
    for section in ("renderables", "overlays"):
        for row in list(render_model.get(section) or []):
            if isinstance(row, dict):
                rows.append(dict(row))
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("semantic_id", "")),
            ",".join(_sorted_strings(row.get("layer_tags") or [])),
            str(row.get("renderable_id", "")),
        ),
    )


def _compute_bounding_box(rows: List[dict]) -> dict | None:
    if not rows:
        return None
    xs: List[int] = []
    ys: List[int] = []
    zs: List[int] = []
    for row in rows:
        transform = dict(row.get("transform") or {})
        position = dict(transform.get("position_mm") or {})
        xs.append(_to_int(position.get("x", 0), 0))
        ys.append(_to_int(position.get("y", 0), 0))
        zs.append(_to_int(position.get("z", 0), 0))
    return {
        "min_mm": {"x": int(min(xs)), "y": int(min(ys)), "z": int(min(zs))},
        "max_mm": {"x": int(max(xs)), "y": int(max(ys)), "z": int(max(zs))},
    }


def build_frame_summary(render_model: dict) -> Tuple[dict, dict]:
    rows = _normalized_renderables(render_model)
    primitive_counts: Dict[str, int] = {}
    layer_counts: Dict[str, int] = {}
    label_count = 0
    for row in rows:
        primitive_type = _primitive_type_from_id(str(row.get("primitive_id", "")))
        primitive_counts[primitive_type] = int(primitive_counts.get(primitive_type, 0)) + 1
        for layer in _sorted_strings(row.get("layer_tags") or []):
            layer_counts[layer] = int(layer_counts.get(layer, 0)) + 1
        label_value = row.get("label")
        label = str(label_value).strip() if isinstance(label_value, str) else ""
        if label:
            label_count += 1

    summary_payload = {
        "schema_version": "1.0.0",
        "render_model_hash": str(render_model.get("render_model_hash", "")),
        "primitive_counts": dict((key, int(primitive_counts[key])) for key in sorted(primitive_counts.keys())),
        "layer_counts": dict((key, int(layer_counts[key])) for key in sorted(layer_counts.keys())),
        "label_count": int(label_count),
        "bounding_box": _compute_bounding_box(rows),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    fingerprint_seed = dict(summary_payload)
    fingerprint_seed["deterministic_fingerprint"] = ""
    summary_payload["deterministic_fingerprint"] = str(canonical_sha256(fingerprint_seed))

    frame_layers = {
        "schema_version": "1.0.0",
        "render_model_hash": str(render_model.get("render_model_hash", "")),
        "layers": [
            {
                "layer_tag": layer,
                "renderable_ids": [
                    str(row.get("renderable_id", ""))
                    for row in rows
                    if layer in set(_sorted_strings(row.get("layer_tags") or []))
                ],
            }
            for layer in sorted(layer_counts.keys())
        ],
    }
    return summary_payload, frame_layers


def render_null_snapshot(
    *,
    render_model: dict,
    out_dir: str,
    renderer_id: str = "null",
    image_width: int = 0,
    image_height: int = 0,
) -> dict:
    model = dict(render_model or {})
    model_hash = str(model.get("render_model_hash", "")).strip() or str(canonical_sha256(model))
    tick = _to_int(model.get("tick", 0), 0)
    viewpoint_id = str(model.get("viewpoint_id", "")).strip() or "viewpoint.unknown"
    pack_lock_hash = str(model.get("pack_lock_hash", "")).strip()
    physics_profile_id = str(model.get("physics_profile_id", "")).strip() or "physics.null"

    summary, frame_layers = build_frame_summary(model)
    summary_hash = str(canonical_sha256(summary))
    snapshot_seed = {
        "render_model_hash": model_hash,
        "renderer_id": str(renderer_id),
        "width": int(max(0, _to_int(image_width, 0))),
        "height": int(max(0, _to_int(image_height, 0))),
        "tick": int(max(0, tick)),
        "viewpoint_id": viewpoint_id,
    }
    snapshot_id = "snapshot.{}".format(str(canonical_sha256(snapshot_seed))[:24])

    output_root = os.path.normpath(os.path.abspath(out_dir))
    snapshot_dir = os.path.join(output_root, str(snapshot_id))
    os.makedirs(snapshot_dir, exist_ok=True)

    summary_path = os.path.join(snapshot_dir, "frame_summary.json")
    layers_path = os.path.join(snapshot_dir, "frame_layers.json")
    snapshot_path = os.path.join(snapshot_dir, "render_snapshot.json")

    with open(summary_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(layers_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(frame_layers, handle, indent=2, sort_keys=True)
        handle.write("\n")

    snapshot_payload = {
        "schema_version": "1.0.0",
        "snapshot_id": snapshot_id,
        "tick": int(max(0, tick)),
        "viewpoint_id": viewpoint_id,
        "render_model_hash": model_hash,
        "pack_lock_hash": pack_lock_hash,
        "physics_profile_id": physics_profile_id,
        "renderer_id": str(renderer_id or "null"),
        "image_width": int(max(0, _to_int(image_width, 0))),
        "image_height": int(max(0, _to_int(image_height, 0))),
        "pixel_format": "NONE",
        "summary_hash": summary_hash,
        "outputs": {
            "image_ref": None,
            "summary_ref": os.path.relpath(summary_path, snapshot_dir).replace("\\", "/"),
            "layers_ref": os.path.relpath(layers_path, snapshot_dir).replace("\\", "/"),
        },
        "extensions": {
            "snapshot_dir": snapshot_dir.replace("\\", "/"),
        },
    }
    with open(snapshot_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(snapshot_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "result": "complete",
        "renderer_id": str(renderer_id or "null"),
        "snapshot_id": snapshot_id,
        "snapshot_dir": snapshot_dir.replace("\\", "/"),
        "snapshot_path": snapshot_path.replace("\\", "/"),
        "summary_hash": summary_hash,
        "summary_path": summary_path.replace("\\", "/"),
        "layers_path": layers_path.replace("\\", "/"),
        "render_snapshot": snapshot_payload,
        "frame_summary": summary,
        "frame_layers": frame_layers,
    }
