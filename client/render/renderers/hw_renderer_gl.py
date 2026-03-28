"""Deterministic hardware renderer backend shim (OpenGL-class) over RenderModel."""

from __future__ import annotations

import os
from typing import Dict, List

from engine.platform.platform_gfx import create_graphics_context, destroy_graphics_context, present_frame
from engine.platform.platform_window import create_window, detect_platform_id

from .software_renderer import render_software_snapshot


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _normalized_backend_policy(backend_policy: dict | None) -> dict:
    policy = dict(backend_policy or {})
    enabled = _sorted_unique_strings(list(policy.get("enabled_backends") or []))
    disabled = _sorted_unique_strings(list(policy.get("disabled_backends") or []))
    if enabled:
        policy["enabled_backends"] = enabled
    if disabled:
        policy["disabled_backends"] = disabled
    return policy


def _default_window_state(*, render_model: dict, width: int, height: int, platform_id: str) -> dict:
    model = dict(render_model or {})
    viewpoint_id = str(model.get("viewpoint_id", "")).strip() or "viewpoint.unknown"
    created = create_window(
        title="Dominium {}".format(viewpoint_id),
        width=int(max(16, _to_int(width, 640))),
        height=int(max(16, _to_int(height, 360))),
        platform_id=detect_platform_id(platform_id),
        resizable=True,
    )
    if str(created.get("result", "")) != "complete":
        return {}
    return dict(created.get("window_state") or {})


def render_hardware_gl_snapshot(
    *,
    render_model: dict,
    out_dir: str,
    image_width: int,
    image_height: int,
    wireframe: bool = False,
    backend_policy: dict | None = None,
    platform_id: str = "",
    window_state: dict | None = None,
) -> Dict[str, object]:
    model = dict(render_model or {})
    width = int(max(16, _to_int(image_width, 640)))
    height = int(max(16, _to_int(image_height, 360)))
    policy = _normalized_backend_policy(backend_policy)
    window = dict(window_state or {})
    if not window:
        window = _default_window_state(
            render_model=model,
            width=width,
            height=height,
            platform_id=platform_id,
        )
    if not window:
        return {
            "result": "refusal",
            "code": "refusal.render.window_create_failed",
            "message": "hardware_gl renderer could not create deterministic platform window state",
        }

    context_result = create_graphics_context(
        window_state=window,
        backend_id="hardware_gl",
        backend_policy=policy,
    )
    if str(context_result.get("result", "")) != "complete":
        return {
            "result": "refusal",
            "code": "refusal.render.backend_unavailable",
            "message": str(context_result.get("message", "hardware_gl backend unavailable under policy")),
            "available_backends": list(context_result.get("available_backends") or []),
        }

    context_state = dict(context_result.get("context_state") or {})
    backend_metadata = {
        "backend_id": "hardware_gl",
        "platform_id": str(context_state.get("platform_id", detect_platform_id(platform_id))).strip(),
        "context_id": str(context_state.get("context_id", "")).strip(),
        "window_id": str(context_state.get("window_id", "")).strip(),
        "surface_size": {
            "width": int(max(16, _to_int(context_state.get("width", width), width))),
            "height": int(max(16, _to_int(context_state.get("height", height), height))),
        },
        "extensions": {},
    }

    snapshot = render_software_snapshot(
        render_model=model,
        out_dir=os.path.normpath(os.path.abspath(out_dir)),
        image_width=width,
        image_height=height,
        wireframe=bool(wireframe),
        renderer_id="hardware_gl",
        backend_metadata=backend_metadata,
    )

    if str(snapshot.get("result", "")) != "complete":
        destroy_graphics_context(context_state=context_state)
        return snapshot

    present_result = present_frame(
        context_state=context_state,
        frame_payload={
            "renderer_id": "hardware_gl",
            "render_model_hash": str((dict(snapshot.get("render_snapshot") or {})).get("render_model_hash", "")),
            "snapshot_id": str(snapshot.get("snapshot_id", "")),
        },
    )
    if str(present_result.get("result", "")) == "complete":
        context_state = dict(present_result.get("context_state") or context_state)

    destroy_result = destroy_graphics_context(context_state=context_state)

    out = dict(snapshot)
    out["renderer_id"] = "hardware_gl"
    out["platform_window_state"] = window
    out["graphics_context_state"] = context_state
    out["present_event"] = dict(present_result.get("present_event") or {})
    out["destroy_event"] = dict(destroy_result.get("event") or {})
    return out
