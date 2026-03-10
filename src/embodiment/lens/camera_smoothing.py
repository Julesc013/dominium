"""Deterministic EMB-2 render-only camera smoothing helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


CAMERA_SMOOTHING_REGISTRY_REL = os.path.join("data", "registries", "camera_smoothing_registry.json")
DEFAULT_CAMERA_SMOOTHING_PARAMS_ID = "cam_smooth.mvp_default"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _vector3_int(value: object) -> dict:
    payload = _as_map(value)
    return {
        "x": int(_as_int(payload.get("x", 0), 0)),
        "y": int(_as_int(payload.get("y", 0), 0)),
        "z": int(_as_int(payload.get("z", 0), 0)),
    }


def _angles_int(value: object) -> dict:
    payload = _as_map(value)
    return {
        "yaw": int(_as_int(payload.get("yaw", 0), 0)),
        "pitch": int(_as_int(payload.get("pitch", 0), 0)),
        "roll": int(_as_int(payload.get("roll", 0), 0)),
    }


def build_camera_smoothing_params_row(
    *,
    camera_smoothing_params_id: str,
    fp_alpha: int,
    tp_alpha: int,
    max_offset: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "camera_smoothing_params_id": str(camera_smoothing_params_id or "").strip(),
        "fp_alpha": int(max(0, min(1000, _as_int(fp_alpha, 0)))),
        "tp_alpha": int(max(0, min(1000, _as_int(tp_alpha, 0)))),
        "max_offset": int(max(0, _as_int(max_offset, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["camera_smoothing_params_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_camera_smoothing_params_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: str(item.get("camera_smoothing_params_id", ""))):
        normalized = build_camera_smoothing_params_row(
            camera_smoothing_params_id=str(row.get("camera_smoothing_params_id", "")).strip(),
            fp_alpha=_as_int(row.get("fp_alpha", 0), 0),
            tp_alpha=_as_int(row.get("tp_alpha", 0), 0),
            max_offset=_as_int(row.get("max_offset", 0), 0),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(normalized.get("camera_smoothing_params_id", "")).strip()
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def camera_smoothing_params_rows_by_id(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    body = _as_map(payload) or _registry_payload(CAMERA_SMOOTHING_REGISTRY_REL)
    rows = _as_list(body.get("camera_smoothing_params")) or _as_list(_as_map(body.get("record")).get("camera_smoothing_params"))
    normalized = normalize_camera_smoothing_params_rows(rows)
    return dict((str(row.get("camera_smoothing_params_id", "")).strip(), dict(row)) for row in normalized if str(row.get("camera_smoothing_params_id", "")).strip())


def camera_smoothing_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(CAMERA_SMOOTHING_REGISTRY_REL))


def _smoothed_position(*, target: Mapping[str, object], previous: Mapping[str, object] | None, alpha: int, max_offset: int) -> dict:
    target_pos = _vector3_int(target)
    if not previous:
        return dict(target_pos)
    previous_pos = _vector3_int(previous)
    offset_limit = max(0, int(max_offset))
    out = {}
    for axis in ("x", "y", "z"):
        delta = int(target_pos[axis]) - int(previous_pos[axis])
        if offset_limit > 0:
            delta = max(-offset_limit, min(offset_limit, delta))
        out[axis] = int(previous_pos[axis]) + ((int(delta) * int(alpha)) // 1000)
    return out


def resolve_smoothed_camera_state(
    *,
    target_camera_state: Mapping[str, object] | None,
    previous_camera_state: Mapping[str, object] | None = None,
    lens_profile_row: Mapping[str, object] | None = None,
    camera_smoothing_params_id: str = DEFAULT_CAMERA_SMOOTHING_PARAMS_ID,
    registry_payload: Mapping[str, object] | None = None,
) -> dict:
    target = _as_map(target_camera_state)
    profile = _as_map(lens_profile_row)
    if not target:
        payload = {"result": "complete", "camera_state": {}, "smoothing_applied": False, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    rows = camera_smoothing_params_rows_by_id(registry_payload)
    smoothing_row = dict(rows.get(str(camera_smoothing_params_id or "").strip()) or rows.get(DEFAULT_CAMERA_SMOOTHING_PARAMS_ID) or {})
    ext = _as_map(profile.get("extensions"))
    camera_mode = str(ext.get("camera_mode", "")).strip()
    if camera_mode == "first_person":
        alpha = int(max(0, min(1000, _as_int(smoothing_row.get("fp_alpha", 1000), 1000))))
    elif camera_mode == "third_person":
        alpha = int(max(0, min(1000, _as_int(smoothing_row.get("tp_alpha", 1000), 1000))))
    else:
        alpha = 1000
    max_offset = int(max(0, _as_int(smoothing_row.get("max_offset", 0), 0)))
    if alpha >= 1000:
        smoothed_state = {
            "position_mm": _vector3_int(target.get("position_mm")),
            "orientation_mdeg": _angles_int(target.get("orientation_mdeg")),
            "view_mode_id": str(target.get("view_mode_id", "")).strip(),
            "view_policy_id": str(target.get("view_policy_id", "")).strip(),
            "lens_id": str(target.get("lens_id", "")).strip(),
            "requires_embodiment": bool(target.get("requires_embodiment", False)),
        }
        applied = False
    else:
        smoothed_state = {
            "position_mm": _smoothed_position(
                target=_as_map(target.get("position_mm")),
                previous=_as_map(previous_camera_state).get("position_mm") if isinstance(previous_camera_state, Mapping) else None,
                alpha=int(alpha),
                max_offset=int(max_offset),
            ),
            "orientation_mdeg": _angles_int(target.get("orientation_mdeg")),
            "view_mode_id": str(target.get("view_mode_id", "")).strip(),
            "view_policy_id": str(target.get("view_policy_id", "")).strip(),
            "lens_id": str(target.get("lens_id", "")).strip(),
            "requires_embodiment": bool(target.get("requires_embodiment", False)),
        }
        applied = True
    payload = {
        "result": "complete",
        "camera_state": dict(smoothed_state),
        "camera_smoothing_params_id": str(smoothing_row.get("camera_smoothing_params_id", "")).strip() or DEFAULT_CAMERA_SMOOTHING_PARAMS_ID,
        "camera_mode": camera_mode or None,
        "smoothing_applied": bool(applied),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
