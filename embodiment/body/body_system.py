"""Deterministic EMB-0 body template and state helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from physics import build_momentum_state


BODY_TEMPLATE_REGISTRY_REL = os.path.join("data", "registries", "body_template_registry.json")
DEFAULT_BODY_TEMPLATE_ID = "template.body.pill"
DEFAULT_FRAME_ID = "frame.world"


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
    current = here
    markers = (
        os.path.join("docs", "canon", "constitution_v1.md"),
        os.path.join("data", "registries"),
        os.path.join("tools", "xstack"),
    )
    while True:
        if all(os.path.exists(os.path.join(current, marker)) for marker in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.normpath(os.path.join(here, "..", "..", ".."))
        current = parent


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError, TypeError):
        return {}
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def build_body_template_row(
    *,
    template_id: str,
    collider_kind: str,
    mass_value: int,
    movement_params_ref: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "template_id": str(template_id or "").strip(),
        "collider_kind": str(collider_kind or "").strip() or "capsule",
        "mass_value": int(max(1, _as_int(mass_value, 1))),
        "movement_params_ref": str(movement_params_ref or "").strip(),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["template_id"]) or (not payload["movement_params_ref"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_body_template_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: str(item.get("template_id", ""))):
        normalized = build_body_template_row(
            template_id=str(row.get("template_id", "")).strip(),
            collider_kind=str(row.get("collider_kind", "capsule")).strip() or "capsule",
            mass_value=_as_int(row.get("mass_value", 1), 1),
            movement_params_ref=str(row.get("movement_params_ref", "")).strip(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        template_id = str(normalized.get("template_id", "")).strip()
        if template_id:
            out[template_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def body_template_rows_by_id(registry_payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    payload = _as_map(registry_payload) or _registry_payload(BODY_TEMPLATE_REGISTRY_REL)
    rows = _as_list(payload.get("body_templates")) or _as_list(_as_map(payload.get("record")).get("body_templates"))
    normalized = normalize_body_template_rows(rows)
    return dict((str(row.get("template_id", "")).strip(), dict(row)) for row in normalized if str(row.get("template_id", "")).strip())


def body_template_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(BODY_TEMPLATE_REGISTRY_REL))


def build_body_state(
    *,
    subject_id: str,
    frame_id: str,
    position_ref: Mapping[str, object] | None,
    orientation_ref: Mapping[str, object] | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "subject_id": str(subject_id or "").strip(),
        "frame_id": str(frame_id or "").strip() or DEFAULT_FRAME_ID,
        "position_ref": _vector3_int(position_ref),
        "orientation_ref": _angles_int(orientation_ref),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["subject_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_body_state_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: str(item.get("subject_id", ""))):
        normalized = build_body_state(
            subject_id=str(row.get("subject_id", "")).strip(),
            frame_id=str(row.get("frame_id", DEFAULT_FRAME_ID)).strip() or DEFAULT_FRAME_ID,
            position_ref=_as_map(row.get("position_ref")),
            orientation_ref=_as_map(row.get("orientation_ref")),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        subject_id = str(normalized.get("subject_id", "")).strip()
        if subject_id:
            out[subject_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def body_state_rows_by_subject_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_body_state_rows(rows)
    return dict((str(row.get("subject_id", "")).strip(), dict(row)) for row in normalized if str(row.get("subject_id", "")).strip())


def body_state_from_body_row(
    *,
    subject_id: str,
    frame_id: str,
    body_row: Mapping[str, object] | None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    body = _as_map(body_row)
    return build_body_state(
        subject_id=str(subject_id or "").strip(),
        frame_id=str(frame_id or DEFAULT_FRAME_ID).strip() or DEFAULT_FRAME_ID,
        position_ref=_as_map(body.get("transform_mm")),
        orientation_ref=_as_map(body.get("orientation_mdeg")),
        extensions=extensions,
    )


def _template_instance_row(*, instance_id: str, template_id: str, created_tick: int, extensions: Mapping[str, object] | None = None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "instance_id": str(instance_id or "").strip(),
        "template_id": str(template_id or "").strip(),
        "instantiation_mode": "micro",
        "created_tick": int(max(0, _as_int(created_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["instance_id"] or not payload["template_id"]:
        return {}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def instantiate_body_system(
    *,
    subject_id: str,
    body_id: str,
    template_id: str = DEFAULT_BODY_TEMPLATE_ID,
    frame_id: str = DEFAULT_FRAME_ID,
    position_mm: Mapping[str, object] | None = None,
    orientation_mdeg: Mapping[str, object] | None = None,
    created_tick: int = 0,
    shard_id: str = "shard.0",
    owner_agent_id: str | None = None,
    controller_id: str | None = None,
    registry_payload: Mapping[str, object] | None = None,
) -> dict:
    templates = body_template_rows_by_id(registry_payload)
    template_row = dict(templates.get(str(template_id).strip()) or {})
    if not template_row:
        template_row = build_body_template_row(
            template_id=DEFAULT_BODY_TEMPLATE_ID,
            collider_kind="capsule",
            mass_value=80000,
            movement_params_ref="move.body.default_ground",
            extensions={
                "capsule": {"radius_mm": 450, "height_mm": 1300},
                "movement_params": {
                    "walk_accel_mm_per_tick2": 120,
                    "look_rate_mdeg_per_tick": 1800,
                    "horizontal_damping_permille": 120,
                },
                "system_template_id": DEFAULT_BODY_TEMPLATE_ID,
                "body_shape_type": "capsule",
            },
        )
    template_ext = _as_map(template_row.get("extensions"))
    capsule = _as_map(template_ext.get("capsule"))
    position = _vector3_int(position_mm)
    orientation = _angles_int(orientation_mdeg)
    subject_token = str(subject_id or "").strip()
    body_token = str(body_id or "").strip()
    owner_agent_token = str(owner_agent_id or "").strip() or (subject_token if subject_token.startswith("agent.") else "")
    template_instance_row = _template_instance_row(
        instance_id="template.instance.body.{}".format(canonical_sha256({"subject_id": subject_token, "body_id": body_token, "template_id": template_id})[:16]),
        template_id=str(template_row.get("template_id", "")).strip(),
        created_tick=int(created_tick),
        extensions={
            "source": "EMB0-3",
            "subject_id": subject_token,
            "body_id": body_token,
            "controller_id": str(controller_id or "").strip() or None,
        },
    )
    body_assembly_row = {
        "assembly_id": body_token,
        "owner_assembly_id": subject_token or body_token,
        "owner_agent_id": owner_agent_token or None,
        "shard_id": str(shard_id or "").strip() or "shard.0",
        "shape_type": str(template_row.get("collider_kind", "capsule")).strip() or "capsule",
        "shape_parameters": {
            "radius_mm": int(max(0, _as_int(capsule.get("radius_mm", 450), 450))),
            "height_mm": int(max(0, _as_int(capsule.get("height_mm", 1300), 1300))),
            "half_extents_mm": {"x": 0, "y": 0, "z": 0},
            "vertex_ref_id": "",
        },
        "collision_layer": "layer.default",
        "dynamic": True,
        "ghost": False,
        "transform_mm": dict(position),
        "orientation_mdeg": dict(orientation),
        "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
        "extensions": {
            "source": "EMB0-3",
            "template_id": str(template_row.get("template_id", "")).strip(),
            "movement_params_ref": str(template_row.get("movement_params_ref", "")).strip(),
            "system_template_id": str(template_ext.get("system_template_id", "")).strip() or str(template_row.get("template_id", "")).strip(),
            "locomotion_state": {
                "grounded": False,
                "jump_cooldown_remaining_ticks": 0,
                "source": "EMB2-3",
            },
        },
    }
    body_state_row = body_state_from_body_row(
        subject_id=subject_token or body_token,
        frame_id=frame_id,
        body_row=body_assembly_row,
        extensions={
            "source": "EMB0-3",
            "body_id": body_token,
            "template_id": str(template_row.get("template_id", "")).strip(),
        },
    )
    momentum_state_row = build_momentum_state(
        assembly_id=body_token,
        mass_value=int(_as_int(template_row.get("mass_value", 80000), 80000)),
        momentum_linear={"x": 0, "y": 0, "z": 0},
        momentum_angular=0,
        last_update_tick=int(max(0, _as_int(created_tick, 0))),
        extensions={
            "source": "EMB0-3",
            "subject_id": subject_token or body_token,
            "template_id": str(template_row.get("template_id", "")).strip(),
        },
    )
    return {
        "result": "complete",
        "body_template": dict(template_row),
        "template_instance_record": dict(template_instance_row),
        "body_assembly": dict(body_assembly_row),
        "body_state": dict(body_state_row),
        "momentum_state": dict(momentum_state_row),
        "movement_params": _as_map(template_ext.get("movement_params")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "template_instance_record": dict(template_instance_row),
                "body_assembly": dict(body_assembly_row),
                "body_state": dict(body_state_row),
                "momentum_state": dict(momentum_state_row),
            }
        ),
    }
