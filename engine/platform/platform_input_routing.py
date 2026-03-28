"""Deterministic platform input routing into interaction command graph surfaces."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from .platform_input import normalize_input_event


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _sorted_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


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

    x, y, z = _rot_z(x, y, z, -yaw)
    x, y, z = _rot_y(x, y, z, -pitch)
    x, y, z = _rot_x(x, y, z, -roll)
    return x, y, z


def _project_point(*, x: float, y: float, z: float, width: int, height: int, fov_deg: float) -> Tuple[float, float, float]:
    if z <= 1.0:
        z = 1.0
    fov = max(20.0, min(120.0, float(fov_deg)))
    focal = (float(height) * 0.5) / math.tan(math.radians(fov * 0.5))
    sx = (float(width) * 0.5) + (x * focal / z)
    sy = (float(height) * 0.5) - (y * focal / z)
    return sx, sy, z


def _normalized_renderables(render_model: dict) -> List[dict]:
    model = dict(render_model or {})
    rows = []
    for section in ("renderables", "overlays"):
        for row in list(model.get(section) or []):
            if not isinstance(row, dict):
                continue
            layer_tags = _sorted_strings(list(row.get("layer_tags") or []))
            if section == "overlays" and "world" not in set(layer_tags):
                continue
            rows.append(dict(row))
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("semantic_id", "")),
            ",".join(_sorted_strings(list(row.get("layer_tags") or []))),
            str(row.get("renderable_id", "")),
        ),
    )


def _primitive_token(primitive_id: str) -> str:
    token = str(primitive_id).strip().lower()
    if token.startswith("prim."):
        parts = token.split(".")
        if len(parts) > 1 and parts[1]:
            return parts[1]
    return "unknown"


def _pick_radius_px(primitive_id: str, z_value: float) -> int:
    primitive = _primitive_token(primitive_id)
    base = {
        "box": 22,
        "sphere": 18,
        "cylinder": 20,
        "capsule": 24,
        "plane": 26,
        "line": 12,
        "glyph": 10,
    }.get(primitive, 16)
    depth_factor = max(0.5, min(2.5, 1400.0 / max(220.0, float(z_value))))
    return int(max(8, min(64, round(base * depth_factor))))


def pick_render_model_target(
    *,
    render_model: dict,
    screen_x: int,
    screen_y: int,
    viewport_width: int,
    viewport_height: int,
    max_pick_radius_px: int = 48,
) -> Dict[str, object]:
    model = dict(render_model or {})
    rows = _normalized_renderables(model)
    if not rows:
        return {
            "result": "refusal",
            "code": "refusal.input.pick_no_renderables",
            "message": "no world-layer renderables available for deterministic picking",
        }

    width = max(16, _to_int(viewport_width, 1280))
    height = max(16, _to_int(viewport_height, 720))
    px = int(_to_int(screen_x, 0))
    py = int(_to_int(screen_y, 0))

    camera = dict((dict(model.get("extensions") or {})).get("camera_viewpoint") or {})
    fov_deg = float(_to_int((dict(model.get("extensions") or {})).get("fov_deg", 60), 60))

    candidates = []
    for row in rows:
        transform = dict(row.get("transform") or {})
        position = dict(transform.get("position_mm") or {})
        x, y, z = _camera_space(position, camera)
        if z <= 5.0:
            continue
        sx, sy, zf = _project_point(x=x, y=y, z=z, width=width, height=height, fov_deg=fov_deg)
        dx = float(sx - px)
        dy = float(sy - py)
        d2 = (dx * dx) + (dy * dy)
        radius = max(int(max_pick_radius_px), _pick_radius_px(str(row.get("primitive_id", "")), zf))
        if d2 > float(radius * radius):
            continue
        semantic_id = str(row.get("semantic_id", "")).strip()
        renderable_id = str(row.get("renderable_id", "")).strip()
        if not semantic_id:
            continue
        candidates.append(
            {
                "semantic_id": semantic_id,
                "renderable_id": renderable_id,
                "distance_sq": float(d2),
                "z_value": float(zf),
            }
        )

    if not candidates:
        return {
            "result": "refusal",
            "code": "refusal.input.pick_miss",
            "message": "no deterministic pick candidate matched click position",
            "pick_position": {"x": int(px), "y": int(py)},
        }

    chosen = sorted(
        candidates,
        key=lambda row: (
            float(row.get("distance_sq", 1e18)),
            float(row.get("z_value", 1e18)),
            str(row.get("semantic_id", "")),
            str(row.get("renderable_id", "")),
        ),
    )[0]
    return {
        "result": "complete",
        "target_semantic_id": str(chosen.get("semantic_id", "")),
        "renderable_id": str(chosen.get("renderable_id", "")),
        "distance_sq": float(chosen.get("distance_sq", 0.0)),
    }


def _camera_look_payload_for_key(key: str) -> dict:
    token = str(key or "").strip().lower()
    mapping = {
        "left": {"delta_yaw_mdeg": -4000, "delta_pitch_mdeg": 0},
        "a": {"delta_yaw_mdeg": -4000, "delta_pitch_mdeg": 0},
        "right": {"delta_yaw_mdeg": 4000, "delta_pitch_mdeg": 0},
        "d": {"delta_yaw_mdeg": 4000, "delta_pitch_mdeg": 0},
        "up": {"delta_yaw_mdeg": 0, "delta_pitch_mdeg": -3000},
        "w": {"delta_yaw_mdeg": 0, "delta_pitch_mdeg": -3000},
        "down": {"delta_yaw_mdeg": 0, "delta_pitch_mdeg": 3000},
        "s": {"delta_yaw_mdeg": 0, "delta_pitch_mdeg": 3000},
    }
    return dict(mapping.get(token) or {})


def route_platform_events_to_commands(
    *,
    input_events: List[dict],
    render_model: dict,
    viewport_width: int,
    viewport_height: int,
    current_target_semantic_id: str = "",
) -> Dict[str, object]:
    normalized = [normalize_input_event(dict(row or {})) for row in list(input_events or []) if isinstance(row, dict)]
    ordered = sorted(
        normalized,
        key=lambda row: (
            int(max(0, _to_int(row.get("tick", 0), 0))),
            int(max(0, _to_int(row.get("sequence", 0), 0))),
            str(row.get("event_type", "")),
            str(row.get("action", "")),
            str(row.get("key", "")),
        ),
    )

    selected_target = str(current_target_semantic_id).strip()
    commands = []

    for row in ordered:
        event_type = str(row.get("event_type", "")).strip().lower()
        if event_type == "input.mouse":
            action = str(row.get("action", "")).strip().lower()
            button = str(row.get("button", "")).strip().lower()
            if action in ("down", "click", "up") and button == "left":
                pick = pick_render_model_target(
                    render_model=render_model,
                    screen_x=_to_int(row.get("x", 0), 0),
                    screen_y=_to_int(row.get("y", 0), 0),
                    viewport_width=int(viewport_width),
                    viewport_height=int(viewport_height),
                )
                if str(pick.get("result", "")) == "complete":
                    selected_target = str(pick.get("target_semantic_id", "")).strip()
                    if selected_target:
                        commands.append(
                            {
                                "command": "interact.select_target",
                                "target_semantic_id": selected_target,
                                "source": "platform.input.mouse",
                            }
                        )
            continue

        if event_type == "input.keyboard":
            action = str(row.get("action", "")).strip().lower()
            key = str(row.get("key", "")).strip().lower()
            if action not in ("down", "press"):
                continue
            if key in ("e", "tab") and selected_target:
                commands.append(
                    {
                        "command": "interact.list_affordances",
                        "target_semantic_id": selected_target,
                        "source": "platform.input.keyboard",
                    }
                )
                continue
            if key in ("enter", "return") and selected_target:
                commands.append(
                    {
                        "command": "interact.execute",
                        "target_semantic_id": selected_target,
                        "affordance_id": "",
                        "parameters": {},
                        "source": "platform.input.keyboard",
                    }
                )
                continue

            look_payload = _camera_look_payload_for_key(key)
            if look_payload:
                commands.append(
                    {
                        "command": "intent.camera_look",
                        "intent_payload": look_payload,
                        "source": "platform.input.keyboard",
                    }
                )

    return {
        "result": "complete",
        "selected_target_semantic_id": str(selected_target),
        "commands": commands,
    }
