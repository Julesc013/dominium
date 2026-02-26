"""Deterministic platform graphics abstraction for presentation surfaces."""

from __future__ import annotations

from typing import List

from tools.xstack.compatx.canonical_json import canonical_sha256

from .platform_window import detect_platform_id


RENDERER_BACKENDS = ("null", "software", "hardware_gl")


def _to_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _sorted_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def list_available_backends(*, platform_id: str = "", backend_policy: dict | None = None) -> List[str]:
    _ = detect_platform_id(platform_id)
    policy = dict(backend_policy or {})
    enabled = _sorted_strings(list(policy.get("enabled_backends") or []))
    disabled = set(_sorted_strings(list(policy.get("disabled_backends") or [])))
    if enabled:
        base = [token for token in enabled if token in RENDERER_BACKENDS]
    else:
        base = list(RENDERER_BACKENDS)
    out = [token for token in base if token not in disabled]
    if "null" not in out:
        out.append("null")
    if "software" not in out:
        out.append("software")
    return sorted(set(out), key=lambda token: ("null", "software", "hardware_gl").index(token) if token in ("null", "software", "hardware_gl") else 99)


def create_graphics_context(
    *,
    window_state: dict,
    backend_id: str,
    backend_policy: dict | None = None,
) -> dict:
    window = dict(window_state or {})
    if bool(window.get("closed", False)):
        return {
            "result": "refusal",
            "code": "refusal.platform.window_closed",
            "message": "cannot create graphics context for a closed window",
        }
    platform_id = detect_platform_id(str(window.get("platform_id", "")))
    requested = str(backend_id or "").strip().lower() or "software"
    available = list_available_backends(platform_id=platform_id, backend_policy=backend_policy)
    if requested not in set(available):
        return {
            "result": "refusal",
            "code": "refusal.render.backend_unavailable",
            "message": "backend '{}' unavailable for current platform policy".format(requested),
            "available_backends": available,
        }
    context_payload = {
        "window_id": str(window.get("window_id", "")),
        "platform_id": platform_id,
        "backend_id": requested,
        "width": int(max(1, _to_int(window.get("width", 1), 1))),
        "height": int(max(1, _to_int(window.get("height", 1), 1))),
    }
    context_id = "gfx.{}".format(canonical_sha256(context_payload)[:16])
    return {
        "result": "complete",
        "context_state": {
            "context_id": context_id,
            "window_id": str(window.get("window_id", "")),
            "platform_id": platform_id,
            "backend_id": requested,
            "width": int(context_payload["width"]),
            "height": int(context_payload["height"]),
            "frame_index": 0,
            "closed": False,
            "extensions": {},
        },
    }


def resize_graphics_surface(*, context_state: dict, width: int, height: int) -> dict:
    context = dict(context_state or {})
    if bool(context.get("closed", False)):
        return {
            "result": "refusal",
            "code": "refusal.platform.context_closed",
            "message": "cannot resize closed graphics context",
        }
    context["width"] = int(max(1, _to_int(width, _to_int(context.get("width", 1), 1))))
    context["height"] = int(max(1, _to_int(height, _to_int(context.get("height", 1), 1))))
    return {"result": "complete", "context_state": context}


def present_frame(*, context_state: dict, frame_payload: dict) -> dict:
    context = dict(context_state or {})
    if bool(context.get("closed", False)):
        return {
            "result": "refusal",
            "code": "refusal.platform.context_closed",
            "message": "cannot present frame on closed graphics context",
        }
    next_index = int(max(0, _to_int(context.get("frame_index", 0), 0))) + 1
    context["frame_index"] = next_index
    fingerprint = canonical_sha256(
        {
            "context_id": str(context.get("context_id", "")),
            "backend_id": str(context.get("backend_id", "")),
            "frame_index": int(next_index),
            "frame_payload": dict(frame_payload or {}),
        }
    )
    return {
        "result": "complete",
        "context_state": context,
        "present_event": {
            "event_type": "gfx.present",
            "context_id": str(context.get("context_id", "")),
            "frame_index": int(next_index),
            "present_fingerprint": str(fingerprint),
        },
    }


def destroy_graphics_context(*, context_state: dict) -> dict:
    context = dict(context_state or {})
    context["closed"] = True
    return {
        "result": "complete",
        "context_state": context,
        "event": {
            "event_type": "gfx.context_destroyed",
            "context_id": str(context.get("context_id", "")),
        },
    }
