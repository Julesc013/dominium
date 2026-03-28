"""Render snapshot capture pipeline over RenderModel artifacts."""

from __future__ import annotations

import json
import os
from typing import Dict

from tools.xstack.compatx.canonical_json import canonical_sha256

from engine.platform.platform_gfx import list_available_backends
from engine.platform.platform_window import detect_platform_id

from .renderers.hw_renderer_gl import render_hardware_gl_snapshot
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


def _write_json(path: str, payload: dict) -> str:
    abs_path = os.path.normpath(os.path.abspath(path))
    parent = os.path.dirname(abs_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return abs_path


def _cache_key(*, render_model_hash: str, renderer_id: str, width: int, height: int, wireframe: bool) -> str:
    payload = {
        "render_model_hash": str(render_model_hash or "").strip(),
        "renderer_id": str(renderer_id or "").strip().lower(),
        "width": int(max(0, _to_int(width, 0))),
        "height": int(max(0, _to_int(height, 0))),
        "wireframe": bool(wireframe),
    }
    return str(canonical_sha256(payload))


def _sorted_unique_strings(values: list[object]) -> list[str]:
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


def _fallback_event(
    *,
    requested_renderer_id: str,
    effective_renderer_id: str,
    available_backends: list[str],
    platform_id: str,
    reason_code: str,
) -> dict:
    return {
        "event_type": "render.backend_fallback",
        "requested_renderer_id": str(requested_renderer_id),
        "effective_renderer_id": str(effective_renderer_id),
        "platform_id": str(platform_id),
        "available_backends": _sorted_unique_strings(list(available_backends or [])),
        "reason_code": str(reason_code),
    }


def _write_fallback_event(*, out_dir: str, cache_key: str, snapshot_id: str, event_payload: dict) -> str:
    root = os.path.normpath(os.path.abspath(out_dir))
    event_dir = os.path.join(root, "_fallback_events")
    os.makedirs(event_dir, exist_ok=True)
    payload = {
        "cache_key": str(cache_key),
        "snapshot_id": str(snapshot_id),
        "fallback_event": dict(event_payload or {}),
    }
    event_path = os.path.join(event_dir, "{}.json".format(str(cache_key)))
    _write_json(event_path, payload)
    return event_path


def _cache_index_load(cache_index_path: str) -> dict:
    payload, err = _load_json(cache_index_path)
    if err:
        return {"entries": {}}
    entries = dict(payload.get("entries") or {})
    return {"entries": dict((str(key), dict(entries[key])) for key in sorted(entries.keys()))}


def _cache_lookup(cache_index_path: str, key: str) -> dict:
    index = _cache_index_load(cache_index_path)
    entries = dict(index.get("entries") or {})
    row = dict(entries.get(str(key)) or {})
    snapshot_path = os.path.normpath(os.path.abspath(str(row.get("snapshot_path", "")).strip()))
    summary_path = os.path.normpath(os.path.abspath(str(row.get("summary_path", "")).strip()))
    if not snapshot_path or not os.path.isfile(snapshot_path):
        return {}
    if not summary_path or not os.path.isfile(summary_path):
        return {}
    return {
        "cache_key": str(key),
        "snapshot_path": snapshot_path,
        "summary_path": summary_path,
        "snapshot_dir": os.path.dirname(snapshot_path),
    }


def _cache_store(cache_index_path: str, key: str, result: dict) -> None:
    index = _cache_index_load(cache_index_path)
    entries = dict(index.get("entries") or {})
    entries[str(key)] = {
        "snapshot_path": str(result.get("snapshot_path", "")).strip(),
        "summary_path": str(result.get("summary_path", "")).strip(),
        "snapshot_id": str(result.get("snapshot_id", "")).strip(),
        "renderer_id": str(result.get("renderer_id", "")).strip(),
    }
    normalized = {"entries": dict((str(cache_key), dict(entries[cache_key])) for cache_key in sorted(entries.keys()))}
    _write_json(cache_index_path, normalized)


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
    cache_dir: str = "",
    backend_policy: dict | None = None,
    platform_id: str = "",
) -> Dict[str, object]:
    requested_renderer = str(renderer_id or "").strip().lower() or "null"
    if requested_renderer not in ("null", "software", "hardware_gl"):
        return {
            "result": "refusal",
            "code": "refusal.render.renderer_not_supported",
            "message": "renderer '{}' is not yet supported by capture pipeline".format(requested_renderer),
        }
    model = dict(render_model or {})
    model_hash = str(model.get("render_model_hash", "")).strip() or str(canonical_sha256(model))
    width_value = max(0, _to_int(width, 0))
    height_value = max(0, _to_int(height, 0))
    platform_token = detect_platform_id(platform_id)
    policy = _normalized_backend_policy(backend_policy)
    available_backends = list_available_backends(platform_id=platform_token, backend_policy=policy)
    renderer = str(requested_renderer)
    fallback = {}
    if requested_renderer not in set(available_backends):
        if requested_renderer in ("hardware_gl",):
            renderer = "software"
            fallback = _fallback_event(
                requested_renderer_id=requested_renderer,
                effective_renderer_id=renderer,
                available_backends=list(available_backends),
                platform_id=platform_token,
                reason_code="refusal.render.backend_unavailable",
            )
        else:
            return {
                "result": "refusal",
                "code": "refusal.render.renderer_not_supported",
                "message": "renderer '{}' is not available under current platform policy".format(requested_renderer),
                "available_backends": list(available_backends),
            }
    cache_root = str(cache_dir or "").strip()
    if not cache_root:
        cache_root = os.path.join(str(out_dir), "_cache")
    cache_root = os.path.normpath(os.path.abspath(cache_root))
    os.makedirs(cache_root, exist_ok=True)
    cache_index_path = os.path.join(cache_root, "snapshot_cache_index.json")
    key = _cache_key(
        render_model_hash=model_hash,
        renderer_id=renderer,
        width=width_value,
        height=height_value,
        wireframe=bool(wireframe),
    )
    hit = _cache_lookup(cache_index_path, key)
    if hit:
        snapshot_payload, snapshot_err = _load_json(hit["snapshot_path"])
        summary_payload, summary_err = _load_json(hit["summary_path"])
        if not snapshot_err and not summary_err:
            out = {
                "result": "complete",
                "cache_hit": True,
                "cache_key": key,
                "renderer_id": str(snapshot_payload.get("renderer_id", renderer)),
                "requested_renderer_id": str(requested_renderer),
                "effective_renderer_id": str(renderer),
                "snapshot_id": str(snapshot_payload.get("snapshot_id", "")),
                "snapshot_dir": str(hit.get("snapshot_dir", "")).replace("\\", "/"),
                "snapshot_path": str(hit.get("snapshot_path", "")).replace("\\", "/"),
                "summary_path": str(hit.get("summary_path", "")).replace("\\", "/"),
                "summary_hash": str(snapshot_payload.get("summary_hash", "")),
                "render_snapshot": snapshot_payload,
                "frame_summary": summary_payload,
            }
            if fallback:
                out["fallback_event"] = dict(fallback)
                event_path = _write_fallback_event(
                    out_dir=str(out_dir),
                    cache_key=key,
                    snapshot_id=str(out.get("snapshot_id", "")),
                    event_payload=fallback,
                )
                out["fallback_event_path"] = event_path.replace("\\", "/")
            return out

    if renderer == "null":
        result = render_null_snapshot(
            render_model=model,
            out_dir=str(out_dir),
            renderer_id="null",
            image_width=width_value,
            image_height=height_value,
        )
    elif renderer == "software":
        software_backend_metadata = {"backend_id": "software"}
        if fallback:
            software_backend_metadata["backend_fallback"] = dict(fallback)
        result = render_software_snapshot(
            render_model=model,
            out_dir=str(out_dir),
            image_width=max(0, _to_int(width, 640)),
            image_height=max(0, _to_int(height, 360)),
            wireframe=bool(wireframe),
            renderer_id="software",
            backend_metadata=software_backend_metadata,
        )
    elif renderer == "hardware_gl":
        result = render_hardware_gl_snapshot(
            render_model=model,
            out_dir=str(out_dir),
            image_width=max(0, _to_int(width, 640)),
            image_height=max(0, _to_int(height, 360)),
            wireframe=bool(wireframe),
            backend_policy=policy,
            platform_id=platform_token,
        )
    else:
        return {
            "result": "refusal",
            "code": "refusal.render.renderer_not_supported",
            "message": "renderer '{}' is not yet supported by capture pipeline".format(renderer),
        }

    if str(result.get("result", "")) != "complete":
        return result
    _cache_store(cache_index_path, key, result)
    out = dict(result)
    out["cache_hit"] = False
    out["cache_key"] = key
    out["cache_index_path"] = cache_index_path.replace("\\", "/")
    out["requested_renderer_id"] = str(requested_renderer)
    out["effective_renderer_id"] = str(renderer)
    if fallback:
        out["fallback_event"] = dict(fallback)
        event_path = _write_fallback_event(
            out_dir=str(out_dir),
            cache_key=key,
            snapshot_id=str(out.get("snapshot_id", "")),
            event_payload=fallback,
        )
        out["fallback_event_path"] = event_path.replace("\\", "/")
    return out
