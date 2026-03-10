"""Deterministic EMB-0 render-only lens transform helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


LENS_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "lens_profile_registry.json")
DEFAULT_LENS_PROFILE_ID = "lens.fp"


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


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError, TypeError):
        return {}
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def build_lens_profile_row(
    *,
    lens_profile_id: str,
    view_mode_id: str,
    view_policy_id: str,
    lens_id: str,
    requires_embodiment: bool,
    required_entitlements: object,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "lens_profile_id": str(lens_profile_id or "").strip(),
        "view_mode_id": str(view_mode_id or "").strip(),
        "view_policy_id": str(view_policy_id or "").strip(),
        "lens_id": str(lens_id or "").strip(),
        "requires_embodiment": bool(requires_embodiment),
        "required_entitlements": _sorted_tokens(required_entitlements),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["lens_profile_id"] or not payload["view_mode_id"] or not payload["lens_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_lens_profile_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: str(item.get("lens_profile_id", ""))):
        normalized = build_lens_profile_row(
            lens_profile_id=str(row.get("lens_profile_id", "")).strip(),
            view_mode_id=str(row.get("view_mode_id", "")).strip(),
            view_policy_id=str(row.get("view_policy_id", "")).strip(),
            lens_id=str(row.get("lens_id", "")).strip(),
            requires_embodiment=bool(row.get("requires_embodiment", False)),
            required_entitlements=row.get("required_entitlements"),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        lens_profile_id = str(normalized.get("lens_profile_id", "")).strip()
        if lens_profile_id:
            out[lens_profile_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def lens_profile_rows_by_id(registry_payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    payload = _as_map(registry_payload) or _registry_payload(LENS_PROFILE_REGISTRY_REL)
    rows = _as_list(payload.get("lens_profiles")) or _as_list(_as_map(payload.get("record")).get("lens_profiles"))
    normalized = normalize_lens_profile_rows(rows)
    return dict((str(row.get("lens_profile_id", "")).strip(), dict(row)) for row in normalized if str(row.get("lens_profile_id", "")).strip())


def lens_profile_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(LENS_PROFILE_REGISTRY_REL))


def resolve_authorized_lens_profile(
    *,
    requested_lens_profile_id: str,
    authority_context: Mapping[str, object] | None,
    registry_payload: Mapping[str, object] | None = None,
) -> dict:
    rows = lens_profile_rows_by_id(registry_payload)
    requested = str(requested_lens_profile_id or "").strip() or DEFAULT_LENS_PROFILE_ID
    profile_row = dict(rows.get(requested) or rows.get(DEFAULT_LENS_PROFILE_ID) or {})
    if not profile_row:
        return {
            "result": "refused",
            "reason_code": "refusal.view.lens_profile_invalid",
            "message": "lens profile is not registered",
            "details": {"lens_profile_id": requested},
        }
    entitlements = set(_sorted_tokens(_as_map(authority_context).get("entitlements") or []))
    required = _sorted_tokens(profile_row.get("required_entitlements") or [])
    missing = [token for token in required if token not in entitlements]
    if missing:
        return {
            "result": "refused",
            "reason_code": "refusal.view.entitlement_missing",
            "message": "lens profile requires additional entitlements",
            "details": {
                "lens_profile_id": str(profile_row.get("lens_profile_id", "")).strip(),
                "missing_entitlements": list(missing),
            },
        }
    return {
        "result": "complete",
        "lens_profile": dict(profile_row),
        "deterministic_fingerprint": canonical_sha256(
            {
                "lens_profile_id": str(profile_row.get("lens_profile_id", "")).strip(),
                "required_entitlements": list(required),
                "authority_entitlements": sorted(entitlements),
            }
        ),
    }


def _rotate_offset(offset_mm: Mapping[str, object], yaw_mdeg: int) -> dict:
    offset = _vector3_int(offset_mm)
    yaw_norm = int(yaw_mdeg) % 360000
    quadrant = int((yaw_norm + 45000) // 90000) % 4
    x = int(offset["x"])
    y = int(offset["y"])
    z = int(offset["z"])
    if quadrant == 0:
        return {"x": x, "y": y, "z": z}
    if quadrant == 1:
        return {"x": -y, "y": x, "z": z}
    if quadrant == 2:
        return {"x": -x, "y": -y, "z": z}
    return {"x": y, "y": -x, "z": z}


def resolve_lens_camera_state(
    *,
    body_state_row: Mapping[str, object] | None,
    body_row: Mapping[str, object] | None,
    lens_profile_row: Mapping[str, object] | None,
    previous_camera_state: Mapping[str, object] | None = None,
) -> dict:
    body_state = _as_map(body_state_row)
    body = _as_map(body_row)
    profile = _as_map(lens_profile_row)
    position = _vector3_int(body_state.get("position_ref") or body.get("transform_mm"))
    orientation = _angles_int(body_state.get("orientation_ref") or body.get("orientation_mdeg"))
    profile_ext = _as_map(profile.get("extensions"))
    offset = _vector3_int(profile_ext.get("follow_offset_mm"))
    camera_mode = str(profile_ext.get("camera_mode", "")).strip()
    if camera_mode in ("first_person", "third_person"):
        rotated_offset = _rotate_offset(offset, int(orientation.get("yaw", 0)))
        target_position = {
            "x": int(position["x"]) + int(rotated_offset["x"]),
            "y": int(position["y"]) + int(rotated_offset["y"]),
            "z": int(position["z"]) + int(rotated_offset["z"]),
        }
        orientation_out = dict(orientation)
    else:
        previous = _as_map(previous_camera_state)
        target_position = _vector3_int(previous.get("position_mm") or position)
        orientation_out = _angles_int(previous.get("orientation_mdeg") or orientation)
    payload = {
        "result": "complete",
        "camera_state": {
            "position_mm": dict(target_position),
            "orientation_mdeg": dict(orientation_out),
            "view_mode_id": str(profile.get("view_mode_id", "")).strip(),
            "view_policy_id": str(profile.get("view_policy_id", "")).strip(),
            "lens_id": str(profile.get("lens_id", "")).strip(),
            "requires_embodiment": bool(profile.get("requires_embodiment", False)),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
