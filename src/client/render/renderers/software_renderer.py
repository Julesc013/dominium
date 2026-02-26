"""Baseline deterministic software renderer (CPU) for RenderModel snapshots."""

from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from .null_renderer import build_frame_summary


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def _sorted_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


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


def _material_map(render_model: dict) -> Dict[str, dict]:
    materials = list((dict(render_model.get("extensions") or {})).get("materials") or [])
    out: Dict[str, dict] = {}
    for row in materials:
        if not isinstance(row, dict):
            continue
        material_id = str(row.get("material_id", "")).strip()
        if not material_id:
            continue
        out[material_id] = dict(row)
    return out


def _rot_x(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    ca = math.cos(angle_rad)
    sa = math.sin(angle_rad)
    return x, (y * ca) - (z * sa), (y * sa) + (z * ca)


def _rot_y(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    ca = math.cos(angle_rad)
    sa = math.sin(angle_rad)
    return (x * ca) + (z * sa), y, (-x * sa) + (z * ca)


def _rot_z(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    ca = math.cos(angle_rad)
    sa = math.sin(angle_rad)
    return (x * ca) - (y * sa), (x * sa) + (y * ca), z


def _camera_space(position_mm: dict, camera_row: dict) -> Tuple[float, float, float]:
    cam_pos = dict(camera_row.get("position_mm") or {})
    cam_ori = dict(camera_row.get("orientation_mdeg") or {})
    x = float(_to_int(position_mm.get("x", 0), 0) - _to_int(cam_pos.get("x", 0), 0))
    y = float(_to_int(position_mm.get("y", 0), 0) - _to_int(cam_pos.get("y", 0), 0))
    z = float(_to_int(position_mm.get("z", 0), 0) - _to_int(cam_pos.get("z", 0), 0))

    yaw = math.radians(float(_to_int(cam_ori.get("yaw", 0), 0)) / 1000.0)
    pitch = math.radians(float(_to_int(cam_ori.get("pitch", 0), 0)) / 1000.0)
    roll = math.radians(float(_to_int(cam_ori.get("roll", 0), 0)) / 1000.0)

    # Inverse camera rotation.
    x, y, z = _rot_z(x, y, z, -yaw)
    x, y, z = _rot_y(x, y, z, -pitch)
    x, y, z = _rot_x(x, y, z, -roll)
    return x, y, z


def _primitive_token(primitive_id: str) -> str:
    token = str(primitive_id).strip().lower()
    if token.startswith("prim."):
        parts = token.split(".")
        if len(parts) > 1 and parts[1]:
            return parts[1]
    return "unknown"


def _project_point(
    *,
    x: float,
    y: float,
    z: float,
    width: int,
    height: int,
    fov_deg: float,
) -> Tuple[float, float, float]:
    if z <= 1.0:
        z = 1.0
    fov = max(20.0, min(120.0, float(fov_deg)))
    focal = (float(height) * 0.5) / math.tan(math.radians(fov * 0.5))
    sx = (float(width) * 0.5) + (x * focal / z)
    sy = (float(height) * 0.5) - (y * focal / z)
    return sx, sy, z


def _draw_rect(
    *,
    pixels: bytearray,
    depth: List[float],
    width: int,
    height: int,
    cx: int,
    cy: int,
    half_w: int,
    half_h: int,
    z_value: float,
    color: Tuple[int, int, int],
    wireframe: bool,
) -> None:
    x0 = _clamp(cx - half_w, 0, width - 1)
    x1 = _clamp(cx + half_w, 0, width - 1)
    y0 = _clamp(cy - half_h, 0, height - 1)
    y1 = _clamp(cy + half_h, 0, height - 1)
    for yy in range(y0, y1 + 1):
        row_idx = yy * width
        for xx in range(x0, x1 + 1):
            if wireframe and not (xx == x0 or xx == x1 or yy == y0 or yy == y1):
                continue
            di = row_idx + xx
            if z_value > depth[di]:
                continue
            depth[di] = z_value
            pi = di * 3
            pixels[pi] = _clamp(color[0], 0, 255)
            pixels[pi + 1] = _clamp(color[1], 0, 255)
            pixels[pi + 2] = _clamp(color[2], 0, 255)


def _draw_circle(
    *,
    pixels: bytearray,
    depth: List[float],
    width: int,
    height: int,
    cx: int,
    cy: int,
    radius: int,
    z_value: float,
    color: Tuple[int, int, int],
    wireframe: bool,
) -> None:
    rr = max(1, radius)
    x0 = _clamp(cx - rr, 0, width - 1)
    x1 = _clamp(cx + rr, 0, width - 1)
    y0 = _clamp(cy - rr, 0, height - 1)
    y1 = _clamp(cy + rr, 0, height - 1)
    r2 = rr * rr
    edge_low = max(0, (rr - 1) * (rr - 1))
    for yy in range(y0, y1 + 1):
        dy = yy - cy
        row_idx = yy * width
        for xx in range(x0, x1 + 1):
            dx = xx - cx
            d2 = (dx * dx) + (dy * dy)
            if d2 > r2:
                continue
            if wireframe and d2 < edge_low:
                continue
            di = row_idx + xx
            if z_value > depth[di]:
                continue
            depth[di] = z_value
            pi = di * 3
            pixels[pi] = _clamp(color[0], 0, 255)
            pixels[pi + 1] = _clamp(color[1], 0, 255)
            pixels[pi + 2] = _clamp(color[2], 0, 255)


def _base_color(material_map: Dict[str, dict], material_id: str) -> Tuple[int, int, int]:
    material = dict(material_map.get(str(material_id).strip()) or {})
    color = dict(material.get("base_color") or {})
    if color:
        return (
            _clamp(_to_int(color.get("r", 160), 160), 0, 255),
            _clamp(_to_int(color.get("g", 160), 160), 0, 255),
            _clamp(_to_int(color.get("b", 160), 160), 0, 255),
        )
    return 160, 160, 160


def _size_px_for_primitive(primitive: str, z_value: float, scale_permille: int) -> int:
    base = {
        "box": 14,
        "sphere": 12,
        "cylinder": 14,
        "capsule": 16,
        "plane": 20,
        "line": 6,
        "glyph": 4,
    }.get(primitive, 10)
    depth_factor = max(0.4, min(2.0, 2000.0 / max(200.0, z_value)))
    scale_factor = max(0.3, min(3.0, float(max(1, _to_int(scale_permille, 1000))) / 1000.0))
    return max(1, int(base * depth_factor * scale_factor))


def _draw_label_marker(
    *,
    pixels: bytearray,
    depth: List[float],
    width: int,
    height: int,
    sx: int,
    sy: int,
    z_value: float,
) -> None:
    # Minimal glyph fallback: a tiny bright rectangle.
    _draw_rect(
        pixels=pixels,
        depth=depth,
        width=width,
        height=height,
        cx=sx,
        cy=max(0, sy - 8),
        half_w=3,
        half_h=2,
        z_value=max(1.0, z_value - 1.0),
        color=(240, 240, 240),
        wireframe=False,
    )


def _write_ppm(path: str, width: int, height: int, pixels: bytes) -> None:
    with open(path, "wb") as handle:
        header = "P6\n{} {}\n255\n".format(int(width), int(height)).encode("ascii")
        handle.write(header)
        handle.write(bytes(pixels))


def render_software_snapshot(
    *,
    render_model: dict,
    out_dir: str,
    image_width: int,
    image_height: int,
    wireframe: bool = False,
) -> dict:
    model = dict(render_model or {})
    model_hash = str(model.get("render_model_hash", "")).strip() or str(canonical_sha256(model))
    tick = max(0, _to_int(model.get("tick", 0), 0))
    viewpoint_id = str(model.get("viewpoint_id", "")).strip() or "viewpoint.unknown"
    pack_lock_hash = str(model.get("pack_lock_hash", "")).strip()
    physics_profile_id = str(model.get("physics_profile_id", "")).strip() or "physics.null"
    width = max(16, _to_int(image_width, 640))
    height = max(16, _to_int(image_height, 360))

    rows = _normalized_renderables(model)
    materials = _material_map(model)
    camera = dict((dict(model.get("extensions") or {})).get("camera_viewpoint") or {})
    fov_deg = float(_to_int((dict(model.get("extensions") or {})).get("fov_deg", 60), 60))

    pixels = bytearray(width * height * 3)
    depth = [1e18] * (width * height)

    for idx, row in enumerate(rows):
        transform = dict(row.get("transform") or {})
        position = dict(transform.get("position_mm") or {})
        scale_permille = _to_int(transform.get("scale_permille", 1000), 1000)
        x, y, z = _camera_space(position_mm=position, camera_row=camera)
        if z <= 5.0:
            continue
        sx_f, sy_f, zf = _project_point(x=x, y=y, z=z, width=width, height=height, fov_deg=fov_deg)
        sx = int(round(sx_f))
        sy = int(round(sy_f))
        if sx < -32 or sy < -32 or sx > width + 32 or sy > height + 32:
            continue
        primitive = _primitive_token(str(row.get("primitive_id", "")))
        size_px = _size_px_for_primitive(primitive, zf, scale_permille)
        color = _base_color(materials, str(row.get("material_id", "")))

        if primitive in ("sphere", "capsule", "cylinder"):
            _draw_circle(
                pixels=pixels,
                depth=depth,
                width=width,
                height=height,
                cx=sx,
                cy=sy,
                radius=size_px,
                z_value=zf + (idx * 0.0001),
                color=color,
                wireframe=bool(wireframe),
            )
        elif primitive == "line":
            _draw_rect(
                pixels=pixels,
                depth=depth,
                width=width,
                height=height,
                cx=sx,
                cy=sy,
                half_w=max(1, size_px),
                half_h=1,
                z_value=zf + (idx * 0.0001),
                color=color,
                wireframe=False,
            )
        elif primitive == "glyph":
            _draw_rect(
                pixels=pixels,
                depth=depth,
                width=width,
                height=height,
                cx=sx,
                cy=sy,
                half_w=2,
                half_h=2,
                z_value=zf + (idx * 0.0001),
                color=color,
                wireframe=False,
            )
        else:
            _draw_rect(
                pixels=pixels,
                depth=depth,
                width=width,
                height=height,
                cx=sx,
                cy=sy,
                half_w=size_px,
                half_h=max(1, size_px // 2),
                z_value=zf + (idx * 0.0001),
                color=color,
                wireframe=bool(wireframe),
            )

        label = str(row.get("label", "")).strip()
        if label:
            _draw_label_marker(
                pixels=pixels,
                depth=depth,
                width=width,
                height=height,
                sx=sx,
                sy=sy,
                z_value=zf + (idx * 0.0001),
            )

    summary, frame_layers = build_frame_summary(model)
    summary_hash = str(canonical_sha256(summary))
    pixel_hash = hashlib.sha256(bytes(pixels)).hexdigest()
    snapshot_seed = {
        "render_model_hash": model_hash,
        "renderer_id": "software",
        "width": int(width),
        "height": int(height),
        "tick": int(tick),
        "viewpoint_id": viewpoint_id,
        "wireframe": bool(wireframe),
    }
    snapshot_id = "snapshot.{}".format(str(canonical_sha256(snapshot_seed))[:24])

    output_root = os.path.normpath(os.path.abspath(out_dir))
    snapshot_dir = os.path.join(output_root, str(snapshot_id))
    os.makedirs(snapshot_dir, exist_ok=True)

    image_path = os.path.join(snapshot_dir, "frame.ppm")
    summary_path = os.path.join(snapshot_dir, "frame_summary.json")
    layers_path = os.path.join(snapshot_dir, "frame_layers.json")
    snapshot_path = os.path.join(snapshot_dir, "render_snapshot.json")

    _write_ppm(path=image_path, width=width, height=height, pixels=bytes(pixels))
    with open(summary_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(layers_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(frame_layers, handle, indent=2, sort_keys=True)
        handle.write("\n")

    snapshot_payload = {
        "schema_version": "1.0.0",
        "snapshot_id": snapshot_id,
        "tick": int(tick),
        "viewpoint_id": viewpoint_id,
        "render_model_hash": model_hash,
        "pack_lock_hash": pack_lock_hash,
        "physics_profile_id": physics_profile_id,
        "renderer_id": "software",
        "image_width": int(width),
        "image_height": int(height),
        "pixel_format": "RGB8",
        "pixel_hash": pixel_hash,
        "summary_hash": summary_hash,
        "outputs": {
            "image_ref": os.path.relpath(image_path, snapshot_dir).replace("\\", "/"),
            "summary_ref": os.path.relpath(summary_path, snapshot_dir).replace("\\", "/"),
            "layers_ref": os.path.relpath(layers_path, snapshot_dir).replace("\\", "/"),
        },
        "extensions": {
            "snapshot_dir": snapshot_dir.replace("\\", "/"),
            "wireframe": bool(wireframe),
        },
    }
    with open(snapshot_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(snapshot_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "result": "complete",
        "renderer_id": "software",
        "snapshot_id": snapshot_id,
        "snapshot_dir": snapshot_dir.replace("\\", "/"),
        "snapshot_path": snapshot_path.replace("\\", "/"),
        "image_path": image_path.replace("\\", "/"),
        "pixel_hash": pixel_hash,
        "summary_hash": summary_hash,
        "summary_path": summary_path.replace("\\", "/"),
        "layers_path": layers_path.replace("\\", "/"),
        "render_snapshot": snapshot_payload,
        "frame_summary": summary,
        "frame_layers": frame_layers,
    }
