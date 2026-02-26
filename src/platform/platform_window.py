"""Deterministic platform window abstraction (presentation-only)."""

from __future__ import annotations

import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


SUPPORTED_PLATFORM_IDS = ("windows", "macos", "linux")


def _to_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _to_float(value: object, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def detect_platform_id(platform_token: str = "") -> str:
    token = str(platform_token or "").strip().lower()
    if token:
        if token in SUPPORTED_PLATFORM_IDS:
            return token
        if token.startswith("win"):
            return "windows"
        if token in ("darwin", "mac", "macos", "osx"):
            return "macos"
        if token.startswith("linux"):
            return "linux"
    runtime = str(sys.platform or "").strip().lower()
    if runtime.startswith("win"):
        return "windows"
    if runtime == "darwin":
        return "macos"
    return "linux"


def create_window(
    *,
    title: str,
    width: int,
    height: int,
    window_id: str = "",
    platform_id: str = "",
    dpi_scale: float = 1.0,
    resizable: bool = True,
) -> dict:
    width_value = max(1, _to_int(width, 1))
    height_value = max(1, _to_int(height, 1))
    platform_value = detect_platform_id(platform_id)
    title_value = str(title or "").strip() or "Dominium"
    dpi_value = max(0.25, min(8.0, _to_float(dpi_scale, 1.0)))
    generated_id = str(window_id or "").strip()
    if not generated_id:
        generated_id = "window.{}".format(
            canonical_sha256(
                {
                    "platform_id": platform_value,
                    "title": title_value,
                    "width": width_value,
                    "height": height_value,
                }
            )[:16]
        )
    return {
        "result": "complete",
        "window_state": {
            "window_id": generated_id,
            "platform_id": platform_value,
            "title": title_value,
            "width": int(width_value),
            "height": int(height_value),
            "dpi_scale": float(dpi_value),
            "resizable": bool(resizable),
            "visible": True,
            "closed": False,
            "extensions": {},
        },
    }


def resize_window(*, window_state: dict, width: int, height: int) -> dict:
    state = dict(window_state or {})
    if bool(state.get("closed", False)):
        return {
            "result": "refusal",
            "code": "refusal.platform.window_closed",
            "message": "cannot resize closed window",
        }
    state["width"] = int(max(1, _to_int(width, _to_int(state.get("width", 1), 1))))
    state["height"] = int(max(1, _to_int(height, _to_int(state.get("height", 1), 1))))
    return {
        "result": "complete",
        "window_state": state,
        "event": {
            "event_type": "window.resize",
            "window_id": str(state.get("window_id", "")),
            "width": int(state.get("width", 1)),
            "height": int(state.get("height", 1)),
        },
    }


def close_window(*, window_state: dict) -> dict:
    state = dict(window_state or {})
    state["closed"] = True
    state["visible"] = False
    return {
        "result": "complete",
        "window_state": state,
        "event": {
            "event_type": "window.closed",
            "window_id": str(state.get("window_id", "")),
        },
    }
