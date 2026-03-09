"""Baseline deterministic software renderer (CPU) for RenderModel snapshots."""

from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Dict, List, Tuple

from src.geo import geo_project
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


def _mix_channel(a: int, b: int, factor_permille: int) -> int:
    factor = _clamp(_to_int(factor_permille, 0), 0, 1000)
    return _clamp((_to_int(a, 0) * (1000 - factor) + _to_int(b, 0) * factor) // 1000, 0, 255)


def _mix_color(a: dict, b: dict, factor_permille: int) -> Tuple[int, int, int]:
    return (
        _mix_channel(dict(a or {}).get("r", 0), dict(b or {}).get("r", 0), factor_permille),
        _mix_channel(dict(a or {}).get("g", 0), dict(b or {}).get("g", 0), factor_permille),
        _mix_channel(dict(a or {}).get("b", 0), dict(b or {}).get("b", 0), factor_permille),
    )


def _screen_permille_to_px(value_permille: object, size: int) -> int:
    return _clamp((_to_int(value_permille, 0) * max(1, int(size))) // 1000, 0, max(0, int(size) - 1))


def _draw_sky_background(*, pixels: bytearray, width: int, height: int, sky_artifact: dict) -> None:
    colors = dict(dict(sky_artifact or {}).get("sky_colors_ref") or {})
    zenith = dict(colors.get("zenith_color") or {"r": 12, "g": 16, "b": 24})
    horizon = dict(colors.get("horizon_color") or {"r": 24, "g": 28, "b": 36})
    for yy in range(max(1, int(height))):
        factor = (yy * 1000) // max(1, int(height) - 1)
        r, g, b = _mix_color(zenith, horizon, factor)
        row_base = yy * width * 3
        for xx in range(max(1, int(width))):
            pi = row_base + (xx * 3)
            pixels[pi] = r
            pixels[pi + 1] = g
            pixels[pi + 2] = b


def _draw_sky_band_rows(
    *,
    pixels: bytearray,
    depth: List[float],
    width: int,
    height: int,
    band_rows: List[dict],
) -> None:
    for idx, row in enumerate(list(band_rows or [])):
        intensity = _clamp(_to_int(row.get("intensity_permille", 0), 0), 0, 1000)
        if intensity <= 0:
            continue
        sx = _screen_permille_to_px(row.get("screen_x_permille", 500), width)
        sy = _screen_permille_to_px(row.get("screen_y_permille", 500), height)
        color = (
            _clamp(18 + (intensity // 10), 0, 255),
            _clamp(24 + (intensity // 8), 0, 255),
            _clamp(42 + (intensity // 6), 0, 255),
        )
        _draw_rect(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            cx=sx,
            cy=sy,
            half_w=max(1, int(width) // 24),
            half_h=max(1, int(height) // 80),
            z_value=1.0e17 + (idx * 0.0001),
            color=color,
            wireframe=False,
        )


def _draw_sky_stars(
    *,
    pixels: bytearray,
    depth: List[float],
    width: int,
    height: int,
    star_rows: List[dict],
) -> None:
    for idx, row in enumerate(list(star_rows or [])):
        sx = _screen_permille_to_px(row.get("screen_x_permille", 500), width)
        sy = _screen_permille_to_px(row.get("screen_y_permille", 500), height)
        color_row = dict(row.get("color") or {})
        color = (
            _clamp(_to_int(color_row.get("r", 230), 230), 0, 255),
            _clamp(_to_int(color_row.get("g", 235), 235), 0, 255),
            _clamp(_to_int(color_row.get("b", 255), 255), 0, 255),
        )
        magnitude = _clamp(_to_int(row.get("magnitude_permille", 500), 500), 0, 1000)
        radius = max(1, 1 + ((1000 - magnitude) // 320))
        _draw_circle(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            cx=sx,
            cy=sy,
            radius=radius,
            z_value=1.0e17 + (idx * 0.0001),
            color=color,
            wireframe=False,
        )


def _draw_sky_disk(
    *,
    pixels: bytearray,
    depth: List[float],
    width: int,
    height: int,
    screen_row: dict,
    color: Tuple[int, int, int],
    radius_px: int,
    z_value: float,
) -> None:
    if not bool(dict(screen_row or {}).get("visible", False)):
        return
    _draw_circle(
        pixels=pixels,
        depth=depth,
        width=width,
        height=height,
        cx=_screen_permille_to_px(dict(screen_row or {}).get("screen_x_permille", 500), width),
        cy=_screen_permille_to_px(dict(screen_row or {}).get("screen_y_permille", 500), height),
        radius=max(1, int(radius_px)),
        z_value=float(z_value),
        color=color,
        wireframe=False,
    )


def _scale_color(color: Tuple[int, int, int], factor_permille: int) -> Tuple[int, int, int]:
    factor = _clamp(_to_int(factor_permille, 1000), 0, 2000)
    return (
        _clamp((int(color[0]) * factor) // 1000, 0, 255),
        _clamp((int(color[1]) * factor) // 1000, 0, 255),
        _clamp((int(color[2]) * factor) // 1000, 0, 255),
    )


def _mix_tuple_color(a: Tuple[int, int, int], b: Tuple[int, int, int], factor_permille: int) -> Tuple[int, int, int]:
    return (
        _mix_channel(int(a[0]), int(b[0]), factor_permille),
        _mix_channel(int(a[1]), int(b[1]), factor_permille),
        _mix_channel(int(a[2]), int(b[2]), factor_permille),
    )


def _tuple_color(value: dict | None, fallback: Tuple[int, int, int]) -> Tuple[int, int, int]:
    row = dict(value or {})
    return (
        _clamp(_to_int(row.get("r", fallback[0]), fallback[0]), 0, 255),
        _clamp(_to_int(row.get("g", fallback[1]), fallback[1]), 0, 255),
        _clamp(_to_int(row.get("b", fallback[2]), fallback[2]), 0, 255),
    )


def _apply_illumination(
    *,
    base_color: Tuple[int, int, int],
    illumination_artifact: dict,
    sx: int,
    sy: int,
    width: int,
    height: int,
) -> Tuple[int, int, int]:
    artifact = dict(illumination_artifact or {})
    if not artifact:
        return base_color
    ext = dict(artifact.get("extensions") or {})
    ambient_intensity = _clamp(_to_int(artifact.get("ambient_intensity", 0), 0), 0, 1000)
    sun_intensity = _clamp(_to_int(artifact.get("sun_intensity", 0), 0), 0, 1000)
    moon_intensity = _clamp(_to_int(artifact.get("moon_intensity", 0), 0), 0, 1000)
    shadow_factor = _clamp(_to_int(artifact.get("shadow_factor", 1000), 1000), 0, 1000)
    ambient_color = _tuple_color(ext.get("ambient_color"), (64, 72, 88))
    key_color = _tuple_color(ext.get("key_light_color"), (255, 240, 220))
    fill_color = _tuple_color(ext.get("fill_light_color"), (112, 120, 136))
    sky_color = _tuple_color(ext.get("sky_light_color"), ambient_color)
    sun_screen = dict(ext.get("sun_screen") or {})
    if bool(sun_screen.get("visible", False)):
        sun_x = _screen_permille_to_px(sun_screen.get("screen_x_permille", 500), width)
        sun_y = _screen_permille_to_px(sun_screen.get("screen_y_permille", 250), height)
        dist = abs(int(sx) - int(sun_x)) + abs(int(sy) - int(sun_y))
        max_dist = max(1, int(width) + int(height))
        directional_factor = _clamp(300 + (((max_dist - min(max_dist, dist)) * 700) // max_dist), 200, 1000)
    else:
        directional_factor = 720
    sun_contrib = (sun_intensity * shadow_factor * directional_factor) // 1_000_000
    moon_contrib = (moon_intensity * 620) // 1000
    total_light = _clamp(max(40, ambient_intensity) + sun_contrib + moon_contrib, 40, 1600)
    lit = _scale_color(base_color, total_light)
    lit = _mix_tuple_color(lit, sky_color, ambient_intensity // 4)
    if sun_contrib > 0:
        lit = _mix_tuple_color(lit, key_color, _clamp((sun_contrib * 3) // 2, 0, 1000))
    if moon_contrib > 0:
        lit = _mix_tuple_color(lit, fill_color, _clamp(moon_contrib, 0, 1000))
    return lit


def _water_cell_sort_key(row: dict) -> tuple:
    key_row = dict(row.get("geo_cell_key") or row.get("tile_cell_key") or {})
    index_tuple = [int(_to_int(item, 0)) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return (
        str(key_row.get("chart_id", "")),
        int(index_tuple[1]),
        int(index_tuple[0]),
        int(index_tuple[2]),
        str(row.get("tile_object_id", "")),
    )


def _water_patch_bounds(
    *,
    row: dict,
    bounds: dict,
    width: int,
    height: int,
    tide_offset_value: int,
) -> tuple[int, int, int, int]:
    key_row = dict(row.get("geo_cell_key") or row.get("tile_cell_key") or {})
    index_tuple = [int(_to_int(item, 0)) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 2:
        index_tuple.append(0)
    min_u = int(bounds.get("min_u", 0))
    max_u = int(bounds.get("max_u", min_u))
    min_v = int(bounds.get("min_v", 0))
    max_v = int(bounds.get("max_v", min_v))
    span_u = max(1, max_u - min_u + 1)
    span_v = max(1, max_v - min_v + 1)
    patch_w = max(2, width // max(2, span_u + 1))
    patch_h = max(2, height // max(6, (span_v * 2) + 2))
    base_left = (width * (index_tuple[0] - min_u)) // span_u
    base_top = (height * 5) // 9 + (((index_tuple[1] - min_v) * ((height * 7) // 20)) // span_v)
    tide_shift = _clamp(_to_int(tide_offset_value, 0) // 6, -4, 4)
    left = _clamp(base_left, 0, max(0, width - patch_w - 1))
    top = _clamp(base_top - tide_shift, 0, max(0, height - patch_h - 1))
    return left, top, patch_w, patch_h


def _water_base_color(
    *,
    water_kind: str,
    tide_offset_value: int,
    sky_artifact: dict,
    illumination_artifact: dict,
) -> tuple[int, int, int]:
    sky_colors = dict(dict(sky_artifact or {}).get("sky_colors_ref") or {})
    illumination_ext = dict(dict(illumination_artifact or {}).get("extensions") or {})
    horizon = _tuple_color(sky_colors.get("horizon_color"), (42, 78, 110))
    sky_light = _tuple_color(illumination_ext.get("sky_light_color"), horizon)
    sun_color = _tuple_color(sky_colors.get("sun_color"), (240, 232, 220))
    if str(water_kind or "") == "river":
        base = (36, 98, 146)
        reflect_factor = 260
    elif str(water_kind or "") == "lake":
        base = (44, 112, 162)
        reflect_factor = 340
    else:
        base = (28, 88, 134)
        reflect_factor = 460
    shimmer = _clamp(260 + abs(int(_to_int(tide_offset_value, 0))), 0, 1000)
    mixed = _mix_tuple_color(base, sky_light, reflect_factor)
    return _mix_tuple_color(mixed, sun_color, shimmer // 3)


def _draw_water_surface_overlay(
    *,
    pixels: bytearray,
    depth: List[float],
    width: int,
    height: int,
    water_artifact: dict,
    sky_artifact: dict,
    illumination_artifact: dict,
) -> None:
    artifact = dict(water_artifact or {})
    ocean_rows = [dict(row) for row in list(artifact.get("ocean_mask_ref") or []) if isinstance(row, dict)]
    river_rows = [dict(row) for row in list(artifact.get("river_mask_ref") or []) if isinstance(row, dict)]
    lake_rows = [dict(row) for row in list(artifact.get("lake_mask_ref") or []) if isinstance(row, dict)]
    if not ocean_rows and not river_rows and not lake_rows:
        return
    all_rows = sorted(ocean_rows + river_rows + lake_rows, key=_water_cell_sort_key)
    us = []
    vs = []
    centers = {}
    for row in all_rows:
        key_row = dict(row.get("geo_cell_key") or row.get("tile_cell_key") or {})
        index_tuple = [int(_to_int(item, 0)) for item in list(key_row.get("index_tuple") or [])]
        while len(index_tuple) < 2:
            index_tuple.append(0)
        us.append(int(index_tuple[0]))
        vs.append(int(index_tuple[1]))
    bounds = {
        "min_u": min(us) if us else 0,
        "max_u": max(us) if us else 0,
        "min_v": min(vs) if vs else 0,
        "max_v": max(vs) if vs else 0,
    }
    for idx, row in enumerate(ocean_rows):
        tide_offset_value = int(_to_int(row.get("tide_offset_value", 0), 0))
        left, top, patch_w, patch_h = _water_patch_bounds(
            row=row,
            bounds=bounds,
            width=width,
            height=height,
            tide_offset_value=tide_offset_value,
        )
        centers[canonical_sha256(dict(row.get("geo_cell_key") or row.get("tile_cell_key") or {}))] = (left + (patch_w // 2), top + (patch_h // 2))
        color = _water_base_color(
            water_kind="ocean",
            tide_offset_value=tide_offset_value,
            sky_artifact=sky_artifact,
            illumination_artifact=illumination_artifact,
        )
        _draw_rect(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            cx=left + (patch_w // 2),
            cy=top + (patch_h // 2),
            half_w=max(1, patch_w // 2),
            half_h=max(1, patch_h // 2),
            z_value=1.0e17 + (idx * 0.0001),
            color=color,
            wireframe=False,
        )
    for idx, row in enumerate(lake_rows):
        tide_offset_value = int(_to_int(row.get("tide_offset_value", 0), 0))
        left, top, patch_w, patch_h = _water_patch_bounds(
            row=row,
            bounds=bounds,
            width=width,
            height=height,
            tide_offset_value=tide_offset_value,
        )
        centers[canonical_sha256(dict(row.get("geo_cell_key") or row.get("tile_cell_key") or {}))] = (left + (patch_w // 2), top + (patch_h // 2))
        color = _water_base_color(
            water_kind="lake",
            tide_offset_value=tide_offset_value,
            sky_artifact=sky_artifact,
            illumination_artifact=illumination_artifact,
        )
        _draw_circle(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            cx=left + (patch_w // 2),
            cy=top + (patch_h // 2),
            radius=max(2, min(patch_w, patch_h) // 2),
            z_value=1.0e17 + 50 + (idx * 0.0001),
            color=color,
            wireframe=False,
        )
    for idx, row in enumerate(river_rows):
        tide_offset_value = int(_to_int(row.get("tide_offset_value", 0), 0))
        left, top, patch_w, patch_h = _water_patch_bounds(
            row=row,
            bounds=bounds,
            width=width,
            height=height,
            tide_offset_value=tide_offset_value,
        )
        center_x = left + (patch_w // 2)
        center_y = top + (patch_h // 2)
        current_hash = canonical_sha256(dict(row.get("geo_cell_key") or row.get("tile_cell_key") or {}))
        centers[current_hash] = (center_x, center_y)
        color = _water_base_color(
            water_kind="river",
            tide_offset_value=tide_offset_value,
            sky_artifact=sky_artifact,
            illumination_artifact=illumination_artifact,
        )
        target_hash = canonical_sha256(dict(row.get("flow_target_tile_key") or {})) if dict(row.get("flow_target_tile_key") or {}) else ""
        target = centers.get(target_hash)
        if target:
            span_w = max(1, abs(int(target[0]) - int(center_x)) // 2)
            span_h = max(1, abs(int(target[1]) - int(center_y)) // 2)
            _draw_rect(
                pixels=pixels,
                depth=depth,
                width=width,
                height=height,
                cx=(center_x + int(target[0])) // 2,
                cy=(center_y + int(target[1])) // 2,
                half_w=max(1, span_w),
                half_h=max(1, min(2, span_h)),
                z_value=1.0e17 + 100 + (idx * 0.0001),
                color=color,
                wireframe=False,
            )
        else:
            _draw_rect(
                pixels=pixels,
                depth=depth,
                width=width,
                height=height,
                cx=center_x,
                cy=center_y,
                half_w=max(1, min(3, patch_w // 5)),
                half_h=max(2, patch_h // 2),
                z_value=1.0e17 + 100 + (idx * 0.0001),
                color=color,
                wireframe=False,
            )


def render_software_snapshot(
    *,
    render_model: dict,
    out_dir: str,
    image_width: int,
    image_height: int,
    wireframe: bool = False,
    renderer_id: str = "software",
    backend_metadata: dict | None = None,
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
    model_extensions = dict(model.get("extensions") or {})
    camera = dict(model_extensions.get("camera_viewpoint") or {})
    fov_deg = float(_to_int(model_extensions.get("fov_deg", 60), 60))
    topology_profile_id = str(model_extensions.get("topology_profile_id", "geo.topology.r3_infinite")).strip() or "geo.topology.r3_infinite"
    projection_profile_id = (
        str(model_extensions.get("projection_profile_id", "geo.projection.perspective_3d")).strip()
        or "geo.projection.perspective_3d"
    )

    pixels = bytearray(width * height * 3)
    depth = [1e18] * (width * height)
    sky_artifact = dict(model_extensions.get("sky_view_artifact") or {})
    illumination_artifact = dict(model_extensions.get("illumination_view_artifact") or {})
    water_artifact = dict(model_extensions.get("water_view_artifact") or {})
    if sky_artifact:
        _draw_sky_background(
            pixels=pixels,
            width=width,
            height=height,
            sky_artifact=sky_artifact,
        )
        _draw_sky_band_rows(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            band_rows=[dict(row) for row in list(sky_artifact.get("milkyway_band_ref") or []) if isinstance(row, dict)],
        )
        sky_colors = dict(sky_artifact.get("sky_colors_ref") or {})
        sky_ext = dict(sky_artifact.get("extensions") or {})
        sun_color_row = dict(sky_colors.get("sun_color") or {"r": 255, "g": 240, "b": 220})
        sun_color = (
            _clamp(_to_int(sun_color_row.get("r", 255), 255), 0, 255),
            _clamp(_to_int(sun_color_row.get("g", 240), 240), 0, 255),
            _clamp(_to_int(sun_color_row.get("b", 220), 220), 0, 255),
        )
        moon_illumination = _clamp(_to_int(sky_ext.get("moon_illumination_permille", 0), 0), 0, 1000)
        moon_shade = 40 + ((moon_illumination * 190) // 1000)
        _draw_sky_disk(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            screen_row=dict(sky_ext.get("sun_screen") or {}),
            color=sun_color,
            radius_px=max(2, min(width, height) // 32),
            z_value=1.0e17,
        )
        _draw_sky_disk(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            screen_row=dict(sky_ext.get("moon_screen") or {}),
            color=(moon_shade, moon_shade, moon_shade),
            radius_px=max(2, min(width, height) // 40),
            z_value=1.0e17 + 0.5,
        )
        _draw_sky_stars(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            star_rows=[dict(row) for row in list(sky_artifact.get("star_points_ref") or []) if isinstance(row, dict)],
        )
    if water_artifact:
        _draw_water_surface_overlay(
            pixels=pixels,
            depth=depth,
            width=width,
            height=height,
            water_artifact=water_artifact,
            sky_artifact=sky_artifact,
            illumination_artifact=illumination_artifact,
        )

    for idx, row in enumerate(rows):
        transform = dict(row.get("transform") or {})
        position = dict(transform.get("position_mm") or {})
        scale_permille = _to_int(transform.get("scale_permille", 1000), 1000)
        projection_result = geo_project(
            position,
            topology_profile_id,
            projection_profile_id,
            projection_request={
                "camera_position_mm": dict(camera.get("position_mm") or {}),
                "camera_orientation_mdeg": dict(camera.get("orientation_mdeg") or {}),
                "viewport_width": int(width),
                "viewport_height": int(height),
                "fov_deg": int(fov_deg),
            },
        )
        projected = dict(projection_result.get("projected_position") or {})
        zf = float(_to_int(projected.get("depth_mm", 0), 0))
        if zf <= 5.0:
            continue
        sx = int(_to_int(projected.get("x_px", 0), 0))
        sy = int(_to_int(projected.get("y_px", 0), 0))
        if sx < -32 or sy < -32 or sx > width + 32 or sy > height + 32:
            continue
        primitive = _primitive_token(str(row.get("primitive_id", "")))
        size_px = _size_px_for_primitive(primitive, zf, scale_permille)
        color = _base_color(materials, str(row.get("material_id", "")))
        color = _apply_illumination(
            base_color=color,
            illumination_artifact=illumination_artifact,
            sx=sx,
            sy=sy,
            width=width,
            height=height,
        )

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
    renderer = str(renderer_id or "software").strip() or "software"
    snapshot_seed = {
        "render_model_hash": model_hash,
        "renderer_id": renderer,
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
        "renderer_id": renderer,
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
            "backend_metadata": dict(backend_metadata or {}),
        },
    }
    with open(snapshot_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(snapshot_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "result": "complete",
        "renderer_id": renderer,
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
